import hashlib
import sys


def getBytes(hexa1, hexa2, attribute_list):
    start_pos = int(hexa1, 16)
    end_pos = int(hexa2, 16)
    length = end_pos - start_pos + 1
    return getAttribute(start_pos, attribute_list, length)

def getAttribute(start_pos, attribute_list, length):
    return_str = ""
    for count in range(0, length):
        if count == length:
            return_str += attribute_list[start_pos + count]
        else:
            return_str += attribute_list[start_pos + count] + " "

    return return_str

def main(mbr):
    mbr_list = mbr.split()
    mbr_end_marker = mbr_list[-2].upper() + " " + mbr_list[-1].upper()
    if mbr_end_marker == "55 AA":
        analyse_mbr(mbr_list)
    else:
        print("MBR End Marker Error")
# function to analyze a disk's MBR

def analyse_mbr(mbr_list):
    print("\n\n**All output WITH SPACES are in HEXADECIMALS and in LITTLE-ENDIAN format**")
    masterbootcode = getBytes("0x0000", "0x01b7", mbr_list)
    disk_identifier = getBytes("0x01b8", "0x01bb", mbr_list)
    partition1 = getBytes("0x01be", "0x01cd", mbr_list)
    partition2 = getBytes("0x01ce", "0x01dd", mbr_list)
    partition3 = getBytes("0x01de", "0x01ed", mbr_list)
    partition4 = getBytes("0x01ee", "0x01fd", mbr_list)

   # print("Master Boot Code: " + masterbootcode)
    print("[+] Disk Identifier: " + disk_identifier)
    print("[+] Partition Entry 1: " + partition1)
    print("[+] Partition Entry 2: " + partition2)
    print("[+] Partition Entry 3: " + partition3)
    print("[+] Partition Entry 4: " + partition4)

    while True:
        partition_no = input("\n\n> Which Partition Entry do you want to read? (1-4): ")
        if partition_no == "1":
            analyse_partition_entry(partition1)
        if partition_no == "2":
            analyse_partition_entry(partition2)
        if partition_no == "3":
            analyse_partition_entry(partition3)
        if partition_no == "4":
            analyse_partition_entry(partition4)
        if partition_no.upper() == "FF":
            analyse_partition_entry(partition4)

def analyse_partition_entry(partition_entry):
    print("======================================")
    print("ANALYSING PARTITION: " + partition_entry)
    partition_entry = partition_entry.split()
    # e.g., DESCRIPTION = (Index, Length)
    STATUS = (1, 1)
    CHS_ADDRESS_START = (2, 3)  # not useful
    PARTITION_TYPE = (5, 1)
    CHS_ADDRESS_END = (6, 3)  # not useful
    FIRST_SECTOR_START = (9, 4)
    NUMBER_OF_SECTORS = (13, 4)

    print("[+] Status: " + partition_entry[STATUS[0] - 1])
    partitionType = getAttribute(PARTITION_TYPE[0] - 1, partition_entry, PARTITION_TYPE[1])
    firstSectorStart = getAttribute(FIRST_SECTOR_START[0] - 1, partition_entry, FIRST_SECTOR_START[1])
    noOfSectors = getAttribute(NUMBER_OF_SECTORS[0] - 1, partition_entry, NUMBER_OF_SECTORS[1])
    print("[+] Partition Type: " + partitionType)
    print("[+] Start of First Sector: " + firstSectorStart + "(First Sector is at LBA {})".format(convertStrHexToInt_littleEndian(firstSectorStart)))
    print("[+] Number of Sectors in Partition: " + noOfSectors + "({} Sectors in Partition)".format(convertStrHexToInt_littleEndian(noOfSectors)))

    choice = input("\n\n> Do you want to analyse this partition? (Y/N)")
    if choice.upper() == "Y":
        analyse_partition(convertStrHexToInt_littleEndian(firstSectorStart),convertStrHexToInt_littleEndian(noOfSectors))

def analyse_partition(startSector, noOfSectors):
    print("======================================")
    print("Go to Sector {}".format(startSector))
    bootsector = input("> Then paste the BOOT SECTOR here: ")
    bootsector = bootsector.split()
    JUMP_INSTRUCTION = getBytes("0x0000", "0x0002", bootsector)
    OEM_IDENTIFIER = getBytes("0x0003", "0x000a", bootsector)
    BIOS_PARAMETER_BLOCK = getBytes("0x000b", "0x0023", bootsector)
    EXTENDED_BIOS_PARAMETER_BLOCK = getBytes("0x0024", "0x0059", bootsector)
    BOOT_CODE = getBytes("0x005a", "0x01fd", bootsector)

    print("\n")
    print("[+] Jump Instruction: " + JUMP_INSTRUCTION)
    print("[+] OEM Identifier: " + OEM_IDENTIFIER)
    print("[+] BIOS Parameter Block (BPB): " + BIOS_PARAMETER_BLOCK)
    print("[+] Extended BIOS Parameter Block (EBPB): " + EXTENDED_BIOS_PARAMETER_BLOCK)
    print("[+] Boot Code: " + BOOT_CODE)

    print("\n-----PRINTING BIOS PARAMETER BLOCK-----")
    # FAT32 BIOS PARAMETER BLOCK (BPB)
    BYTES_PER_SECTOR = getBytes("0x0b", "0x0c", bootsector)
    SECTOR_PER_CLUSTER = getBytes("0x0d", "0x0d", bootsector)
    NUM_OF_RESERVED_SECTORS = getBytes("0x0e", "0x0f", bootsector)
    NUM_OF_FAT = getBytes("0x10", "0x10", bootsector)
    MEDIA_DESCRIPTOR_TYPE = getBytes("0x15", "0x15", bootsector)
    TOTAL_SECTORS = getBytes("0x13", "0x14", bootsector)
    SECTORS_PER_TRACK = getBytes("0x18", "0x19", bootsector)
    NUM_OF_HEADS = getBytes("0x1a", "0x1b", bootsector)
    NUM_OF_SECTORS_BEFORE_PART = getBytes("0x1c", "0x1f", bootsector)
    TOTAL_SECTORS2 = getBytes("0x20", "0x23", bootsector)  # only has value TOTAL_SECTORS >> 65536
    print("[+] Bytes Per Sector: " + BYTES_PER_SECTOR + "({} bytes)".format(convertStrHexToInt_littleEndian(BYTES_PER_SECTOR)))
    print("[+] Sector Per Cluster: " + SECTOR_PER_CLUSTER + "({} sectors)".format(convertStrHexToInt_littleEndian(SECTOR_PER_CLUSTER)))
    cluster_size = int(convertStrHexToInt_littleEndian(BYTES_PER_SECTOR)) * int(convertStrHexToInt_littleEndian(SECTOR_PER_CLUSTER))
    print("[+] Number of Reserved Sectors: " + NUM_OF_RESERVED_SECTORS + "({} sectors)".format(convertStrHexToInt_littleEndian(NUM_OF_RESERVED_SECTORS)))
    print("[+] Number of File Allocation Tables (usually 2): " + NUM_OF_FAT + "({})".format(convertStrHexToInt_littleEndian(NUM_OF_FAT)))

    mdt = ""
    if MEDIA_DESCRIPTOR_TYPE.strip().upper() == "F8":
        mdt = "non-removeable media"
    elif MEDIA_DESCRIPTOR_TYPE.strip().upper() == "F0":
        mdt = "removeable media"
    print("[+] Media Descriptor Type: " + MEDIA_DESCRIPTOR_TYPE + "({})".format(mdt))

    print("[+] Total Number of Sectors (should be <65536, and excluding reserved sectors): " + TOTAL_SECTORS + "({} sectors)".format(convertStrHexToInt_littleEndian(TOTAL_SECTORS)))
    print("[+] Sectors Per Track: " + SECTORS_PER_TRACK + "({} sectors)".format(convertStrHexToInt_littleEndian(SECTORS_PER_TRACK)))
    print("[+] Number of Heads: " + NUM_OF_HEADS + "({})".format(convertStrHexToInt_littleEndian(NUM_OF_HEADS)))
    print("[+] Number of Sectors (before this partition): " + NUM_OF_SECTORS_BEFORE_PART + "({} sectors )".format(convertStrHexToInt_littleEndian(NUM_OF_SECTORS_BEFORE_PART)))
    print("[+] Total Number of Sectors (if >65536, and excluding reserved sectors): " + TOTAL_SECTORS2 + "({} sectors)".format(convertStrHexToInt_littleEndian(TOTAL_SECTORS2)))

    # FAT32 EXTENDED BIOS PARAMETER BLOCK (EBPB)
    print("\n-----PRINTING EXTENDED BIOS PARAMETER BLOCK-----")
    SIZE_OF_ONE_FAT = getBytes("0x24", "0x27", bootsector)
    FAT32_EXTRA_FLAGS = getBytes("0x28", "0x29", bootsector)
    FAT_VERS_NO = getBytes("0x2b", "0x2b", bootsector)
    CLUSTER_NO_OF_ROOT = getBytes("0x2c", "0x2f", bootsector)
    SECTOR_NO_OF_FSINFO = getBytes("0x30", "0x31", bootsector)
    COPY_OF_BOOTRECORD = getBytes("0x32", "0x33", bootsector)
    X13_DRIVE_NUM = getBytes("0x40", "0x40", bootsector)
    RESERVED = getBytes("0x41", "0x41", bootsector)
    EXTENDED_BOOT_SIG = getBytes("0x42", "0x42", bootsector)
    VOL_SERIAL_NUM = getBytes("0x43", "0x46", bootsector)
    VOL_LABEL = getBytes("0x47", "0x51", bootsector)
    INF_FILESYSTEM_IDENTIFIER = getBytes("0x52", "0x59", bootsector)

    print("[+] Size of 1 File Allocation Table, in Sectors: " + SIZE_OF_ONE_FAT + "({} sectors)".format(convertStrHexToInt_littleEndian(SIZE_OF_ONE_FAT)))
    print("[+] FAT32 Extra Flags: " + FAT32_EXTRA_FLAGS + "({})".format(convertStrHexToInt_littleEndian(FAT32_EXTRA_FLAGS)))
    print("[+] FAT Version Number: " + FAT_VERS_NO + "({})".format(convertStrHexToInt_littleEndian(FAT_VERS_NO)))
    print("[+] Cluster # of the Root Directory's first cluster: " + CLUSTER_NO_OF_ROOT + "(Cluster #{})".format(convertStrHexToInt_littleEndian(CLUSTER_NO_OF_ROOT)))
    print("[+] Sector # of the FSInfo Structure in the Reserved Area: " + SECTOR_NO_OF_FSINFO + "(Sector #{})".format(convertStrHexToInt_littleEndian(SECTOR_NO_OF_FSINFO)))
    print("[+] If non-zero, Sector # in the reserved area containing a copy of the boot record: " + COPY_OF_BOOTRECORD + "(Sector #{})".format(convertStrHexToInt_littleEndian(COPY_OF_BOOTRECORD)))
    driv_num = ""
    if X13_DRIVE_NUM.strip().upper() == "00":
        driv_num = "Floppy Disks"
    elif X13_DRIVE_NUM.strip().upper() == "80":
        driv_num = "Hard Disks"
    print("[+] INT 0x13 Drive Number: " + X13_DRIVE_NUM + "({})".format(driv_num))
    print("[+] Reserved, used by Windows NT: " + RESERVED)
    print("[+] Extended Boot Signature: " + EXTENDED_BOOT_SIG)
    print("[+] Volume Serial Number: " + VOL_SERIAL_NUM)
    print("[+] 11-byte Volume Label: " + VOL_LABEL)
    print("[+] Informational Filesystem Identifier String: " + INF_FILESYSTEM_IDENTIFIER)

    print("\n-----Additional Calculation for you!-----")
    # calculating cluster size (bytes per sector)
    print("[++] Cluster Size (Bytes/Sector * Sectors/Cluster): " + str(cluster_size) + " bytes")

    # calculating start of root directory
    # start sector + reserved sectors + num of FAT * size of FAT
    sector_location = int(startSector) + int(convertStrHexToInt_littleEndian(NUM_OF_RESERVED_SECTORS)) + (int(convertStrHexToInt_littleEndian(NUM_OF_FAT)) * int(convertStrHexToInt_littleEndian(SIZE_OF_ONE_FAT)))
    print("[++] Sector Location of Root Directory (from start of Disk): " + str(sector_location))

    # start sector + (CLUSTER# - 2) * SECTORS/CLUSTER
    new_sector_location = sector_location + ((int(convertStrHexToInt_littleEndian(CLUSTER_NO_OF_ROOT))) - 2) * int(convertStrHexToInt_littleEndian(SECTOR_PER_CLUSTER))
    print("If Root Directory Cluster # is not 2, check: " + str(new_sector_location))

    print("\n-----FAT32 Partition should look something like this now-----")
    print("|------------------------------------------|")
    print("|--------------Boot Sector-----------------|")
    print("|-------------Sector {} to {}--------------|".format(int(startSector), int(startSector) + 1))
    print("|------------------------------------------|")
    print("|-----Boostrap Code/FSINFO Sector, etc-----|")
    print("|-------------Sector {} to {}--------------|".format(int(startSector) + 1, int(startSector) + int(convertStrHexToInt_littleEndian(NUM_OF_RESERVED_SECTORS)) - 1))
    print("|------------------------------------------|")
    print("|----------File Allocation Table 1---------|")
    FAT1_start = int(startSector) + int(convertStrHexToInt_littleEndian(NUM_OF_RESERVED_SECTORS))
    FAT1_end = int(startSector) + int(convertStrHexToInt_littleEndian(NUM_OF_RESERVED_SECTORS)) + int(convertStrHexToInt_littleEndian(SIZE_OF_ONE_FAT))
    print("|-------------Sector {} to {}--------------|".format(FAT1_start, FAT1_end - 1))
    print("|------------------------------------------|")
    print("|----------File Allocation Table 2---------|")
    FAT2_start = FAT1_end
    FAT2_end = FAT1_end + int(convertStrHexToInt_littleEndian(SIZE_OF_ONE_FAT))
    print("|-------------Sector {} to {}--------------|".format(FAT2_start, FAT2_end - 1))
    print("|------------------------------------------|")
    print("|----------------Data Area-----------------|")
    print("|-------------Sector {} to {}--------------|".format(sector_location, "end of partition"))
    print("|------------------------------------------|")


# convert hex (little endian) in string format to int
def convertStrHexToInt_littleEndian(hex):
    big_endian = ""
    for b in reversed(hex.split()):
        big_endian += b

    # convert big endian hex value to int
    return str(int(big_endian, 16))

if __name__ == "__main__":
    mbr = sys.argv[1]
    main(mbr)