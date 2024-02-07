#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

using namespace std;

int main() {
    // Set URL and target server
    string url = "https://api.example.com/restricted-resource";
    string host = url.substr(8, url.find("/", 8) - 8);

    // Create socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        cerr << "Error creating socket" << endl;
        return 1;
    }

    // Set server address
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr(host.c_str());
    servaddr.sin_port = htons(443); // HTTPS port

    // Connect to server
    if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
        cerr << "Error connecting to server" << endl;
        close(sockfd);
        return 1;
    }

    // Create GET request (including HTTP headers)
    string request = "GET /restricted-resource HTTP/1.1\r\n";
    request += "Host: " + host + "\r\n";
    request += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36\r\n";
    request += "Connection: close\r\n";
    request += "\r\n";

    // Send request
    if (send(sockfd, request.c_str(), request.length(), 0) < 0) {
        cerr << "Error sending request" << endl;
        close(sockfd);
        return 1;
    }

    // Receive response
    vector<char> buffer(1024);
    int bytes_received = recv(sockfd, buffer.data(), buffer.size(), 0);
    if (bytes_received < 0) {
        cerr << "Error receiving response" << endl;
        close(sockfd);
        return 1;
    }

    // Parse response (extract status code)
    string response(buffer.data(), bytes_received);
    string status_line = response.substr(0, response.find("\r\n"));
    string status_code = status_line.substr(status_line.find(" ") + 1, status_line.find(" ", status_line.find(" ") + 1) - (status_line.find(" ") + 1));

    // Print status code
    cout << "Status code: " << status_code << endl;

    // Close connection
    close(sockfd);

    return 0;
}
