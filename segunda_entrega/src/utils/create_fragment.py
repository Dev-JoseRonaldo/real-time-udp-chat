import struct # Bilioteca que Interpreta bytes como dados binários compactados

from utils.checksum import find_checksum

def create_fragment(contents, fragSize, fragIndex, fragCount, seq_num, ack_num):
    data = bytearray() # Estrtura de dados do tipo bytearray
    data.extend(contents[:fragSize]) # Pegando um fragmento de tamanho fragSize

    header_no_checksum = struct.pack('!IIIII', fragSize, fragIndex, fragCount, seq_num, ack_num) # Header compactado sem o checksum
    fragment_no_checksum = header_no_checksum + bytearray(data) # fragmento sem o checksum

    checksum = find_checksum(fragment_no_checksum) # Gerandos checksum
    checksum = int(checksum,2)
    header = struct.pack('!IIIIII', fragSize, fragIndex, fragCount, seq_num, ack_num, checksum) # Header compactado com checksum

    fragment = header + bytearray(data) # Fragmento completo (com checksum)

    return fragment