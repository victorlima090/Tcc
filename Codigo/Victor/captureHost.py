# By Klenilmar Dias

import argparse
import pcapy
import dpkt
import featureExtraction2 as featureExtraction
import curses
import signal
import sys
from collections import deque
from sklearn import svm
from sklearn.externals import joblib

count = 0
previous_timestamp = 0
pred_total_0 = 0
pred_total_1 = 0
actual_total_0 = 0
actual_total_1 = 0
tp = 0
fn = 0
fp = 0
tn = 0


def parseArgs():
    parser = argparse.ArgumentParser(description='Real time streaming video classification')
    parser.add_argument('-w', '--window_size', help='Window size', required=False)
    return parser.parse_args()


def convert_header_to_ts(header):
    timestamp = header.getts()
    return timestamp[0] + 1e-6 * timestamp[1]


def process_packet(window_packets):
    global previous_timestamp, model, count
    
    (timestamp, packet) = window_packets[0]

    eth = dpkt.ethernet.Ethernet(packet)
    ip = eth.data

    # somente pacotes IPs sao suportados
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        return
            
    # contagem de pacotes de incremento
    count = count + 1

    # definir timestamp pela primeira vez
    if previous_timestamp == 0:
        previous_timestamp = timestamp

    # coletar caracteristicas de cada pacote
    (inter_packet_time, packet_size, ip_len, ip_header_len, ip_off, ip_protocol, ip_ttl) = featureExtraction.extractStandardFeatures(packet, timestamp, previous_timestamp)
    previous_timestamp = timestamp

    # coletar caracteristicas de um grupo de pacotes (janela de comprimento W=3)
    (mean_ia_time, var_ia_time, mean_ip, var_ip, mean_ttl, var_ttl, mean_p, var_p) = featureExtraction.extractWindowFeatures(window_packets)

    # fazer predicao (faz o teste com novas caracteristicas capturadas em tempo real)
    features = [inter_packet_time, packet_size, ip_len, ip_off, ip_protocol, ip_ttl, mean_ia_time, var_ia_time, mean_ip, var_ip, mean_ttl, var_ttl, mean_p, var_p]
    pred = model.predict([features]) # Prever saida (apos treinamento). O modelo treinado no script train.py, pode ser usado para prever novos valores

    # determinar a categoria real (actual)
    actual = 0
    if featureExtraction.isNetflixPacket(ip) or featureExtraction.isYoutubePacket(ip):
        actual = 1

    return pred, actual


def update_stats(stdscr, pred, actual):
    global count
    global pred_total_0, pred_total_1
    global actual_total_0, actual_total_1
    global tp, fn, fp, tn
    
    true_p = 0
    false_p = 0
    true_n = 0
    false_n = 0
    
    # contagem de erros
    if pred[0] == 0: 
        pred_total_0 = pred_total_0 + 1

        if actual == 0:
            actual_total_0 = actual_total_0 + 1
            tn = tn + 1
        else:
            actual_total_1 = actual_total_1 + 1
            fn = fn + 1
    else:
        pred_total_1 = pred_total_1 + 1

        if actual == 0:
            actual_total_0 = actual_total_0 + 1
            fp = fp + 1
        else:
            actual_total_1 = actual_total_1 + 1
            tp = tp + 1

    # calcular taxas true / false
    if actual_total_0 > 0:
        true_n = float(tn) / actual_total_0
        false_p = float(fp) / actual_total_0
    if actual_total_1 > 0:
        true_p = float(tp) / actual_total_1
        false_n = float(fn) / actual_total_1


    # atualiza o display
    stdscr.addstr(7, 0, "Total de Pacotes: %5d" % count)
    stdscr.addstr(8, 0, "Acuracia     : %f" % ((tp+tn)/float(count)))

    stdscr.addstr(10,  0, "Pred.  video: %5d        Pred.  outros: %5d" % (pred_total_1, pred_total_0))
    stdscr.addstr(11, 0, "Atual video: %5d        Atual outros: %5d" % (actual_total_1, actual_total_0))

    stdscr.addstr(13, 0, "True positive : %f   True negative : %f" % (true_p, true_n))
    stdscr.addstr(14, 0, "False positive: %f   False negative: %f" % (false_p, false_n))

    stdscr.refresh()


def sig_handler(signal, frame):
    curses.endwin()
    sys.exit(0)


def main():
    global model 

    window_packets = deque()
    window_size = 3
    count = 0
    capture_device = 'h1-eth0'

    # configurar manipulador de sinal
    signal.signal(signal.SIGINT, sig_handler)

    # analisar argumentos
    args = parseArgs()
    if None != args.window_size and 0 < int(args.window_size):
        window_size = int(args.window_size)

    # carrega o modelo do classificador treinado (reconstroi um arquivo Persistido com "joblib.dump")
    model = joblib.load('model/model.pkl')

    # inicializar o display
    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.noecho()
    curses.cbreak()
    window = stdscr.subwin(4, 70, 0, 0)
    window.addstr(1, 7, 'Classificador de Trafego de Streaming de Video Online', curses.color_pair(1))
    window.addstr(2, 18, 'Versao Beta (by Klenilmar)', curses.color_pair(1))
    window.border()
    window.refresh()
    stdscr.addstr(4, 0, 'Dispositivo de Captura: %s' % capture_device)

    
    # iniciar captura ao vivo (em tempo real)
    capture = pcapy.open_live(capture_device, 65536, 1, 0)

    # build window_size-1 window of packets first
    while (len(window_packets) < window_size-1):
        header, packet = capture.next()
        eth = dpkt.ethernet.Ethernet(packet)
        if eth.type == dpkt.ethernet.ETH_TYPE_IP:
            window_packets.append((convert_header_to_ts(header), packet))

    # fazer previsao nos pacotes recebidos
    while (1):
        header, packet = capture.next()

        eth = dpkt.ethernet.Ethernet(packet)
        if eth.type == dpkt.ethernet.ETH_TYPE_IP:
            window_packets.append((convert_header_to_ts(header), packet))
            pred, actual = process_packet(window_packets)
            update_stats(stdscr, pred, actual)
            window_packets.popleft()


main()

