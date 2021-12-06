#include "main.h"


int main() {
    while (true) {
        Menu();
        std::string option;
        std::cin >> option;

        Data* pDataObject = NULL;

        switch(option[0]) {
            case '1':
                pDataObject = CreateDataSaverEntry();
                break;
            case '2':
                pDataObject = GetDataSaverEntry();
                break;
            case '3':
                DeleteDataSaverEntry();
                break;
            case '4':
                ViewEntriesList();
                break;
            case '5':
                exit(0);
            default:
                std::cout << "{-} Invalid option!" << std::endl;
                exit(0);
        }

        if (pDataObject != NULL) {
            DataObjectHandler(pDataObject);
        }
    }

    return 0;
};


void Menu(void) {
    std::cout << "++==++ Data Saver ++==++" << std::endl; 
    std::cout << "-----  Main menu  -----" << std::endl;
    std::cout << "1. Create data saver entry" << std::endl;
    std::cout << "2. Get data saver entry" << std::endl;
    std::cout << "3. Delete data saver entry" << std::endl;
    std::cout << "4. View entries list" << std::endl;
    std::cout << "5. Exit" << std::endl;
    std::cout << "> ";
};

void DataMenu(void) {
    std::cout << "++==++ Data Saver ++==++" << std::endl;
    std::cout << "------ Entry menu ------" << std::endl;
    std::cout << "1. Save data" << std::endl;
    std::cout << "2. View saved data" << std::endl;
    std::cout << "3. Redact saved data" << std::endl;
    std::cout << "4. Delete saved data" << std::endl;
    std::cout << "5. Exit to main menu" << std::endl;
    std::cout << "> ";
};

int DataObjectHandler(Data* pObj) {
    while (true) {
        DataMenu();
        
        std::string option;
        std::cin >> option;

        switch(option[0]) {
            case '1':
                pObj->SaveData();
                break;
            case '2':
                pObj->ViewData();
                break;
            case '3':
                pObj->RedactData();
                break;
            case '4':
                pObj->DelData();
                break;
            case '5':
                return 0;
            default:
                std::cout << "{-} Invalid option!" << std::endl;
                exit(0);
        }
    }
    return 0;
}

Data* CreateDataSaverEntry() {
    Data* pObj = new Data();

    if (pObj == NULL) {
        std::cout << "{-} Can't create new object of class Data!" << std::endl;
        return NULL;
    }
    
    uint32_t NewEntryIdx = DataObjectList.size();
    pObj->SetIdx(NewEntryIdx);
    DataObjectList.push_back(pObj);
 
    std::cout << "{+} Entry created with id <" << NewEntryIdx << ">" << std::endl;
    
    return pObj;
};

Data* GetDataSaverEntry() {
    std::cout << "{?} Enter entry id: ";
    uint32_t EntryId;
    std::cin >> EntryId;

    if (EntryId >= DataObjectList.size()) {
        std::cout << "{-} Invalid entry id!" << std::endl;
        return NULL;
    }

    return DataObjectList[EntryId];
};

int DeleteDataSaverEntry() {
    std::cout << "{?} Enter entry id: ";
    uint32_t EntryId;
    std::cin >> EntryId;

    if (EntryId >= DataObjectList.size()) {
        std::cout << "{-} Invalid entry id!" << std::endl;
        return 0;
    }

    if (DataObjectList[EntryId] != NULL) {
        delete DataObjectList[EntryId]; // vuln here, UAF
        //DataObjectList[EntryId] = NULL; // vuln fix
    } else {
        std::cout << "{-} No entry with this id!" << std::endl;
        return 0;
    }

    return 1;
};

int ViewEntriesList() {
    for (auto i : DataObjectList)
        i->ViewEntry();
    
    return 0;
};

void DecodeHex(uint8_t* Input, uint8_t* Output, uint32_t OutSize) {
    for (int i = 0; i < OutSize; i++) {
        char tmp[2] = {(char)Input[i*2], (char)Input[i*2+1]};
        Output[i] = strtol(tmp, NULL, 16);
    }
}

void PrintHexData(uint8_t* Input, uint32_t InputSize) {
    for (int i = 0; i < InputSize; i++) {
        printf("%02x", Input[i]);
    }
    std::cout << std::endl;    
};

Data::Data() {
    isUsed = true;
};

Data::~Data() {
    isUsed = false;
    if (m_key)
        delete[] m_key;
    if (m_data) 
        delete[] m_data;
}

int Data::SaveData() {
    std::cout << "-- Encryption algorithm --" << std::endl;
    std::cout << "1. No encryption" << std::endl;
    std::cout << "2. Xor encrytion" << std::endl;
    std::cout << "3. RC4" << std::endl;
    std::cout << "{?} Choose encryption algorithm: ";

    std::string option;
    std::cin >> option;

    switch (option[0]) {
        case '1':
            m_encAlgo = PLAIN;
            break;
        case '2':
            m_encAlgo = XOR;
            break;
        case '3':
            m_encAlgo = RC4;
            break;
        default:
            std::cout << "{-} Invalid option!" << std::endl;
            return 0;
    }

    std::cout << "{?} Enter key size: ";
    std::cin >> m_keySize;

    switch (m_encAlgo) { 
        case PLAIN:
            pEncryptHandler = NULL;
            pDecryptHandler = NULL;
            break;
        case XOR:
            pEncryptHandler = &XorEncryption;
            pDecryptHandler = &XorEncryption;
            break;
        case RC4:
            pEncryptHandler = &RC4Encryption;
            pDecryptHandler = &RC4Encryption;
            break;
    }

    uint8_t* TmpBuffer = new uint8_t[m_keySize*2 + 1];
    m_key = new uint8_t[m_keySize];

    std::cout << "{?} Enter key (in hex): ";
    std::cin >> TmpBuffer;

    DecodeHex(TmpBuffer, m_key, m_keySize);

    delete[] TmpBuffer;

    std::cout << "{?} Entrer data size: ";
    std::cin >> m_dataSize;

    if (m_dataSize <= 0) {
        std::cout << "{-} Incorrect data size!" << std::endl;
        return 0;
    }

    TmpBuffer = new uint8_t[m_dataSize*2 + 1];
    m_data = new uint8_t[m_dataSize];

    std::cout << "{?} Enter data (in hex): ";
    std::cin >> TmpBuffer;
    DecodeHex(TmpBuffer, m_data, m_dataSize);

    delete[] TmpBuffer;

    std::cout << "{!} Your key: " << m_key << std::endl;
    std::cout << "{!} Your data: " << m_data << std::endl;

    Encrypt();

    std::cout << "{!} Your encrypted data (in hex): ";
    PrintHexData(m_data, m_dataSize);

    return 0;
};

int Data::DelData() {
    if (m_key) 
        delete[] m_key;
    if (m_data)
        delete[] m_data;

    m_keySize = 0;
    m_dataSize = 0;
    isUsed = false;
    m_idx = 0;
    m_encAlgo = PLAIN;

    std::cout << "{!} Data is deleted!" << std::endl;
    return 0;
};

void Data::ViewEntry() {
    std::cout << "-- Entry #" << m_idx << " --" << std::endl;
    std::cout << "Algo: ";

    switch (m_encAlgo) {
        case PLAIN:
            std::cout << "No encryption" << std::endl;
            break;
        case XOR:
            std::cout << "XOR" << std::endl;
            break;
        case RC4:
            std::cout << "RC4" << std::endl;
            break;
        default:
            std::cout << "Undefined" << std::endl;
            break;
    }

    std::cout << "Key size: " << m_keySize << std::endl;
    std::cout << "Data size: " << m_dataSize << std::endl;
    std::cout << "Used: ";

    if (isUsed) 
        std::cout << "true" << std::endl;
    else 
        std::cout << "false" << std::endl;
};

int Data::ViewData() {
    std::cout << "{!} Your data: ";
    
    Decrypt();
    PrintHexData(m_data, m_dataSize);
    Encrypt();

    return 0;
};

int Data::RedactData() {
    std::cout << "{?} Enter start offset: ";
    uint32_t off = 0;
    std::cin >> off;

    if (off >= m_dataSize) {
        std::cout << "{-} Invalid offset!" << std::endl;
        return 1;
    }

    std::cout << "{?} Enter size of data: ";
    uint32_t size = 0;
    std::cin >> size;

    if (off + size >= m_dataSize) {
        std::cout << "{-} Invalid size!" << std::endl;
        return 1;
    }

    uint8_t* TmpBuffer = new uint8_t[size * 2 + 1];
    uint8_t* DecodedBuffer = new uint8_t[size];

    std::cout << "{?} Enter data (in hex): ";
    std::cin >> TmpBuffer;

    DecodeHex(TmpBuffer, DecodedBuffer, size);
    Decrypt();

    for (int i = off; i < off + size; i++) {
        m_data[i] = DecodedBuffer[i];
    }

    delete[] TmpBuffer;
    delete[] DecodedBuffer;

    Encrypt();
    std::cout << "{!} Data is redacted!" << std::endl;

    return 0;
};


void XorEncryption(Data* pObj) {
    for (int i = 0; i < pObj->GetDataSize(); i++) {
        pObj->SetDataByte(i, pObj->GetDataByte(i) ^ pObj->GetKeyByte(i % pObj->GetKeySize()));
    }
};

void RC4Encryption(Data* pObj) {
    struct rc4_state *rc4_ctx = new struct rc4_state;
    rc4_setup(rc4_ctx, pObj->GetKey(), pObj->GetKeySize());
    rc4_crypt(rc4_ctx, pObj->GetData(), pObj->GetDataSize());
    delete rc4_ctx;
};
