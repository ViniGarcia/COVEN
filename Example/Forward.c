#include <stdlib.h>
#include <stdio.h>

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(int argc, char const *argv[])
{
    int clientConf, clientSocket;
    struct sockaddr_in clientAddress;
    int cliendAddLen = sizeof(clientAddress);
    int socketOption = 1;

    int serverSocket;
    struct sockaddr_in serverAddress;
    int serverAddLen = sizeof(serverAddress);

    int dataBufferLen;
    char dataBuffer[1600] = {0};

    //Server configuration
    if ((clientConf = socket(AF_INET, SOCK_STREAM, 0)) == 0) exit(-1);
    if (setsockopt(clientConf, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &socketOption, sizeof(socketOption))) exit(-2);
    clientAddress.sin_family = AF_INET;
    clientAddress.sin_addr.s_addr = INADDR_ANY;
    clientAddress.sin_port = htons(8012);
    if (bind(clientConf, (struct sockaddr *)&clientAddress, sizeof(clientAddress))<0) exit(-3);
    if (listen(clientConf, 3) < 0) exit(-4);
    if ((clientSocket = accept(clientConf, (struct sockaddr *)&clientAddress,(socklen_t*)&cliendAddLen))<0) exit(-5);

    //Client configuration
    if ((serverSocket = socket(AF_INET, SOCK_STREAM, 0)) == 0) exit(-6);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(8013);
    if (connect(serverSocket, (struct sockaddr *)&serverAddress, sizeof(struct sockaddr)) == -1) exit(-7);

    while(1){
      dataBufferLen = read(clientSocket , dataBuffer, 1516);
      printf("OK3!! %d\n", dataBufferLen);
      send(serverSocket , dataBuffer , dataBufferLen , 0);
    }
    return 0;
}
