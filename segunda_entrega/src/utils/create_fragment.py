import struct # Bilioteca que Interpreta bytes como dados binários compactados
from zlib import crc32 # Calcula uma soma de verificação CRC 32 bits

def create_fragment(contents, fragSize, fragIndex, fragCount):
    data = bytearray() # Estrtura de dados do tipo bytearray
    data.extend(contents[:fragSize]) # Pegando um fragmento de tamanho fragSize
    
    header_no_checksum = struct.pack('!III', fragSize, fragIndex, fragCount) # Header compactado sem o checksum
    fragment_no_checksum = header_no_checksum + bytearray(data) # fragmento sem o checksum

    checksum = crc32(fragment_no_checksum) # Gerando uma soma de verificação CRC como checksum
    header = struct.pack('!IIII', fragSize, fragIndex, fragCount, checksum) # Header compactado com checksum
    fragment = header + bytearray(data) # Fragmento completo (com checksum)

    return fragment