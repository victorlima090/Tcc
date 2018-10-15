# By Klenilmar & Mateus
# -*- Coding: utf8 -*-
#coding: utf-8

import dpkt
import argparse
import sys
import ipaddress
import socket
import numpy as np


# Analisar argumentos de entrada (utiliza o modulo de analise de linha de comando "argparse")
def parseArgs():
    parser = argparse.ArgumentParser(description='Parse a PCAP file')
    parser.add_argument('-f', '--file', help='.pcap file', required=True)
    parser.add_argument('-c', '--count', help='Packet count', required=False)
    parser.add_argument('-w', '--window_size', help='Window size', required=False)
    
    return parser.parse_args()


# Funcao converte endereco CIDR para endereco Subnet
def cidrToSubnet(cidr):
    return ipaddress.IPv4Network(cidr)


# Funcao identifica enderecos IPs (origem/destino) provenientes de provedores de servicos Youtube
def isYoutubePacket(ip):
    ## Usar esses dois comandos no caso dos comando nao comentados nao funcionar
    ## Isso e um problema que pode depender de cada maquina onde o Script vai rodar
    # dest_ip_addr = ipaddress.IPv4Address(socket.inet_ntoa(ip.dst))
    # src_ip_addr = ipaddress.IPv4Address(socket.inet_ntoa(ip.src))
    dest_ip_addr = ipaddress.IPv4Address(ip.dst)
    src_ip_addr = ipaddress.IPv4Address(ip.src)

    if dest_ip_addr in cidrToSubnet(unicode('173.194.0.0/16')) or \
                    dest_ip_addr in cidrToSubnet(unicode('74.125.0.0/16')) or \
                    dest_ip_addr in cidrToSubnet(unicode('192.178.0.0')) or \
                    dest_ip_addr in cidrToSubnet(unicode('192.179.0.0/16')) or \
                    dest_ip_addr in cidrToSubnet(unicode('172.217.0.0/16')) or \
                    dest_ip_addr in cidrToSubnet(unicode('216.58.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('173.194.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('74.125.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('192.178.0.0')) or \
                    src_ip_addr in cidrToSubnet(unicode('192.179.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('172.217.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('216.58.0.0/16')):

        # Identifica o Protocolo de Transporte  que carrega o Protocolo IP
        if ip.p == 17:
            udp = ip.data
            if udp.dport == 443 or udp.sport == 443:
                return True
        elif ip.p == 6:
            tcp = ip.data
            if tcp.dport == 443 or tcp.sport == 443:
                return True

    return False


# Funcao identifica enderecos IPs (origem/destino) provenientes de provedores de servicos Netflix
def isNetflixPacket(ip):
    ## Usar esses dois comandos no caso dos comando nao comentados nao funcionar
    ## Isso e um problema que pode depender de cada maquina onde o Script vai rodar
    # dest_ip_addr = ipaddress.IPv4Address(socket.inet_ntoa(ip.dst)) 
    # src_ip_addr = ipaddress.IPv4Address(socket.inet_ntoa(ip.src))
    dest_ip_addr = ipaddress.IPv4Address(ip.dst)
    src_ip_addr = ipaddress.IPv4Address(ip.src)

    if dest_ip_addr in cidrToSubnet(unicode('54.192.0.0/16')) or \
                    dest_ip_addr in cidrToSubnet(unicode('23.246.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('54.192.0.0/16')) or \
                    src_ip_addr in cidrToSubnet(unicode('23.246.0.0/16')):

        # Identifica o Protocolo de Transporte que carrega o Protocolo IP
        if ip.p == 17:
            udp = ip.data
            if udp.dport == 443 or udp.sport == 443:
                return True
        elif ip.p == 6:
            tcp = ip.data
            if tcp.dport == 443 or tcp.sport == 443:
                return True

    return False


## As caracterisitcas (features) extraidas foram divididas em dois grupos:
# Grupo1: caracteristicas  (features) extraidas de cada pacote (extractStandardFeatures)
# Grupo2: caracteristicas (features) extraidas de um grupo de pacotes(extractWindowFeatures)

# Funcao para extrai caracteristicas provenientes de cada Pacote (parametros encontrados nos campos de cabecalho IPv4)
def extractStandardFeatures(packet, timestamp, previous_timestamp):
    eth = dpkt.ethernet.Ethernet(packet) # Analisar o pacote. Decodifica o pacote Ethernet
    ip = eth.data

    # Somente Pacotes IP sao suportados
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        return -1

    inter_packet_time = timestamp - previous_timestamp
    packet_size = len(packet)
    ip_len = ip.len
    ip_header_len = ip.hl
    ip_off = ip.off
    ip_protocol = ip.p
    ip_ttl = ip.ttl

    return (inter_packet_time, packet_size, ip_len, ip_header_len, ip_off, ip_protocol, ip_ttl)


# Funcao para extrai caracteristicas provenientes de um grupo de Pacotes (parametros encontrados nos campos de cabecalho IPv4 a partir de mais de um Pacote IP)
def extractWindowFeatures(packets):
    previous_arrival_time = 0
    interarrival_times = []
    ip_sizes = []
    ttls = []
    protocols = []

    # Coletar dados para cada pacote
    for pktBuf in packets:

        timestamp = pktBuf[0]
        eth = dpkt.ethernet.Ethernet(pktBuf[1]);
        ip = eth.data

        # tempo medio de chegada
        if previous_arrival_time != 0:
            interarrival_times.append(timestamp - previous_arrival_time)
        previous_arrival_time = timestamp

        # comprimento medio do IP
        ip_sizes.append(ip.len)

        # TTL medio (TTL - Time To Live)
        ttls.append(ip.ttl)

        # protocolo medio
        protocols.append(ip.p)

    return calcAverages(interarrival_times, ip_sizes, ttls, protocols)


# Funcao calcula Media e Varianca dos campos extraidos do Grupo2
def calcAverages(interarrival_times, ip_sizes, ttls, protocols):
    if len(interarrival_times) > 0:
        mean_interarrival_time = np.mean(interarrival_times)
        var_interarrival_time = np.var(interarrival_times)
    else:
        mean_interarrival_time = 0
        var_interarrival_time = 0
    mean_ip_size = np.mean(ip_sizes)
    var_ip_size = np.var(ip_sizes)
    mean_ttl = np.mean(ttls)
    var_ttl = np.var(ttls)
    mean_protocol = np.mean(protocols)
    var_protocol = np.var(protocols)

    return (mean_interarrival_time, var_interarrival_time, mean_ip_size, var_ip_size, mean_ttl, var_ttl, mean_protocol,
            var_protocol)


# Funcao Principal
def main():
    # analisar argumentos de entrda
    args = parseArgs()
    name = args.file
    f = open(name)
    g = open(name)
    if None != args.count:
        maxCount = int(args.count)
    else:
        maxCount = -1
    if None != args.window_size:
        window_size = int(args.window_size)
    else:
        window_size = 3 # Tamanho da janela de Pacotes IP que o extrator considera (W=3)

    # locais de contagem de pacotes
    count = 0
    previous_timestamp = 0
    target_count = 0
    total_count = 0

    # abrir aquivos com a funcao "open" utilizando o argumento "w" que diz que queremos abrir o arquivo para escrita (gravar dados)
    featureFile = open('featureMatrix.dat', 'w')
    categoryFile = open('category.dat', 'w')
    #Analise de arquivos PCAP e dos pacotes contidos neles.
    pcap = dpkt.pcap.Reader(f) # Pega um objeto de arquivo para ler registro do arquivo (para isso utiliza a classe "Reader")
    pktList = pcap.readpkts() # Retorna uma lista de tuplas recebidas em um buffer
    pcap = dpkt.pcap.Reader(g)

    for ts,buf in pcap:
        total_count = total_count + 1
        print "Processando Pacotes: ", total_count
        eth = dpkt.ethernet.Ethernet(buf) # Desempacota o quadro Ethernet
        ip = eth.data

        # Apenas pacotes IPs sao suportados 
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        if count == 0:
            previous_timestamp = ts

        # coleta caracteristicas
        (inter_packet_time, packet_size, ip_len, ip_header_len, ip_off, ip_protocol, ip_ttl) = extractStandardFeatures(
            buf, ts, previous_timestamp)
        previous_timestamp = ts

        # coletar caracteristica a partir da proxima janela de pacotes
        # construir array do proximo pacote para extrair caracteristicas de
        skip_count = 0
        window_packets = []
        for x in range(0, window_size):
            index = (total_count - 1) + x + skip_count

            # verifica limites
            if (index >= len(pktList)):
                break

            # apenas pacotes IP sao suportados
            # se um pacote nao-IP for encontrado, ignora-lo
            eth = dpkt.ethernet.Ethernet(pktList[index][1]);
            while eth.type != dpkt.ethernet.ETH_TYPE_IP:
                skip_count = skip_count + 1
                index = (total_count - 1) + x + skip_count

                # verifica limites
                if (index >= len(pktList)):
                    break

                eth = dpkt.ethernet.Ethernet(pktList[index][1]);

            # add to window arrays
            if (index < len(pktList)):
                window_packets.append(pktList[index])

        (mean_ia_time, var_ia_time, mean_ip, var_ip, mean_ttl, var_ttl, mean_p, var_p) = extractWindowFeatures(
            window_packets)

        # determina a categoria do pacote
        category = 0
        if isNetflixPacket(ip) or isYoutubePacket(ip):
        #if isYoutubePacket(ip):
            category = 1
            target_count = target_count + 1

        # escreve (grava) as informacoes de features e category nos seus respectivos arquivos
        featureFile.write('%f %d %d %d %d %d %f %f %f %f %f %f %f %f\n' % (
        inter_packet_time, packet_size, ip_len, ip_off, ip_protocol, ip_ttl, mean_ia_time, var_ia_time, mean_ip, var_ip,
        mean_ttl, var_ttl, mean_p, var_p))
        categoryFile.write('%d\n' % category)

        count = count + 1
        # faz a checagem do numero maximo de pacotes
        if maxCount != -1 and count >= maxCount:
            break

    print "Target count: ", target_count
    print "IP count:  ", count
    print "Total count: ", total_count
    featureFile.close()
    categoryFile.close()


if __name__ == '__main__':
    main()




