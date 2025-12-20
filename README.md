SecureChat: Encrypted Chat Backend – Detailed Overview and mapout

-------------------------------------------------------------------------------------------------------------------------------------
Version: 1.0 Author: Bathist Date: 20/12/2025
Legality and other important info is mentioned at the bottom and must be seen
-------------------------------------------------------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------------------------------------------------------
Overview
-------------------------------------------------------------------------------------------------------------------------------------
SecureChat is a system designed for secure, encrypted communication, specifically targeting a scenario where a company utilizes a standard, web-based interface (a “decoy” site) while the true, secure chat functionality is handled by a separate client application running through a command-line interface (CLI). This approach minimizes the attack surface and provides a layer of separation.

-------------------------------------------------------------------------------------------------------------------------------------
Architecture – Deep Dive
-------------------------------------------------------------------------------------------------------------------------------------
The architecture is now divided into two key components:

Decoy Website (UI): This is a standard, visually-appealing website – e.g., for a company’s internal portal. It serves as a visual distraction and provides a user-friendly interface without any actual encryption or secure communication. Users interact with this site for other company functions, and it doesn’t directly handle the chat.

Secure Client (CLI): This is a Python script that only handles the secure, encrypted communication.

Key Exchange: The Python script initiates the Diffie-Hellman key exchange with the server, establishing the shared secret key.
Encryption/Decryption: The Python script encrypts and decrypts messages using the shared key.
WebSocket Connection: Manages the persistent WebSocket connection to the server. This is the only component communicating securely.
Server-Side Python Backend: This component remains the same - acting as a message router and dispatcher. It solely receives encrypted messages from the CLI client and forwards them to the intended recipients.
-------------------------------------------------------------------------------------------------------------------------------------
Key Technologies
-------------------------------------------------------------------------------------------------------------------------------------
Python: (Flask or Django) - Web framework for the backend.
JavaScript: (For the Decoy Website) - ES6+ - For the web frontend.
websockets: Library for WebSocket communication.

Diffie-Hellman Algorithm: The cryptographic foundation for key exchange.
AES (Advanced Encryption Standard): A symmetric encryption algorithm for message encryption.
Security Considerations (Critical)

Diffie-Hellman Implementation: Crucially, choose a well-vetted, secure implementation of the Diffie-Hellman algorithm.
    AES Key Management: Securely store and manage the AES key on the server.

Network Segmentation: Isolate the secure client (CLI) from the decoy website's network. Implement firewall rules to restrict access.

Input Validation: Sanitize all user input on both the CLI client and server.

Rate Limiting: Implement rate limiting to prevent denial-of-service attacks.
Workflow

A user accesses the decoy website.
The CLI client (running in the background) remains connected to the server via the secure WebSocket connection.
The user types a message in the CLI and sends it.
The CLI encrypts the message and sends it to the server.
The server decrypts the message and forwards it to the intended recipient(s).

-------------------------------------------------------------------------------------------------------------------------------------

@2025 - Made by bathist

This system is only for educational use and the owner holds no responsibility for which use the client and server owner have with this and their intentions. ( see Rules and Legal Disclaimer for more infomation ) 
(All rights reserved. Bathist, december 2025)

-------------------------------------------------------------------------------------------------------------------------------------

Legal Disclaimer - 
IMPORTANT: READ CAREFULLY BEFORE USING SECURECHAT.

-------------------------------------------------------------------------------------------------------------------------------------

- RULES AND LEGAL DISCLAIMER - 

By using SecureChat, you acknowledge and agree to the following terms and conditions:

1. Limited Warranty & No Guarantee of Security:
-------------------------------------------------------------------------------------------------------------------------------------
SecureChat is provided “as is” and “as available.” Bathist makes no warranties, express or implied, regarding its performance, reliability, functionality, or security.

While we have implemented security measures, including the Diffie-Hellman key exchange and AES encryption, we cannot guarantee the absolute security or confidentiality of your communications. No system is entirely immune to compromise.
Use of SecureChat is at your own risk. You are solely responsible for taking any measures necessary to protect your data and communications.
Bathist does not guarantee that SecureChat will be uninterrupted or error-free.
-------------------------------------------------------------------------------------------------------------------------------------
2. User Responsibility:

You are responsible for:
Maintaining the confidentiality of your AES key. Loss or compromise of this key will render your communications insecure.
Implementing appropriate security measures on your end (e.g., secure storage of the key, firewall configuration).
Understanding and complying with all applicable laws and regulations related to communication and data protection.
You are responsible for any damage or loss resulting from the misuse of SecureChat.
-------------------------------------------------------------------------------------------------------------------------------------
3. Limited Liability:

Bathist shall not be liable for any direct, indirect, incidental, special, or consequential damages arising from the use of SecureChat, including but not limited to, loss of profits, data loss, or interruption of service.
Bathist’s total liability for any claim arising out of the use of SecureChat shall not exceed the amount paid by you for access to SecureChat (if applicable).
-------------------------------------------------------------------------------------------------------------------------------------
4. Decoy Website Disclaimer:

The Decoy Website is a visual aid for user interaction and does not participate in or secure any communication. Do not rely on the Decoy Website for secure data transmission.
-------------------------------------------------------------------------------------------------------------------------------------
5. Changes to Disclaimer:

Bathist reserves the right to modify this disclaimer at any time without prior notice. It is your responsibility to review this disclaimer periodically.
-------------------------------------------------------------------------------------------------------------------------------------
6. Governing Law:

This disclaimer shall be governed by and construed in accordance with the laws of:
England and Wales: For initial development and operations, this disclaimer is primarily governed by the laws of England and Wales.
United States of America: To the extent SecureChat is used by individuals or entities within the United States, this disclaimer shall also be subject to the laws of the relevant state(s) of the United States of America. (Specific state laws may apply).
@2025 - Made by bathist
7. Contact Information:

Anonomous - no contant infomations, sorry.

-------------------------------------------------------------------------------------------------------------------------------------

@2025 - Made by bathist

-------------------------------------------------------------------------------------------------------------------------------------