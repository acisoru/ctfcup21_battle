#include <iostream>
#include <vector>
#include <fstream>
#include <cstdint>
#include <sstream>
#include <string>

#include "RC4.h"

void setup();
void Menu();
void DecodeHex(uint8_t*, uint8_t*, uint32_t);
void PrintHexData(uint8_t*, uint32_t);
void DataMenu();

enum ENCRYPTION_TYPE {
    PLAIN,
    XOR,
    RC4
};

class Data {
    private:
        uint8_t* m_data;
        uint8_t* m_key;
        uint32_t m_keySize;
        uint32_t m_dataSize;
        uint8_t isUsed;
        uint32_t m_idx;
        ENCRYPTION_TYPE m_encAlgo;
        void (*pEncryptHandler)(Data*);
        void (*pDecryptHandler)(Data*);
    public:
        Data();
        ~Data();

        int SaveData();
        int ViewData();
        int RedactData();
        int DelData();
        void ViewEntry();
        void SetIdx(uint32_t idx) { m_idx = idx; };
        void SetDataByte(uint32_t idx, uint8_t byte) { 
            m_data[idx] = byte;
        };
        uint8_t GetDataByte(uint32_t idx) { return m_data[idx]; };
        uint8_t GetKeyByte(uint32_t idx) { return m_key[idx]; };
        uint32_t GetDataSize() { return m_dataSize; };
        uint32_t GetKeySize() { return m_keySize; };
        uint8_t* GetKey() { return m_key; };
        uint8_t* GetData() { return m_data; };

        void Encrypt() {
            if (pEncryptHandler != NULL)
                pEncryptHandler(this);
        }

        void Decrypt() {
            if (pDecryptHandler != NULL)
                pDecryptHandler(this);
        }
        
};

int DataObjectHandler(Data* pObj);

std::vector<Data*> DataObjectList;
Data* CreateDataSaverEntry();
Data* GetDataSaverEntry();
int DeleteDataSaverEntry();
int ViewEntriesList();

void XorEncryption(Data* pObj);
void RC4Encryption(Data* pObj);