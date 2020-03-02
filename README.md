COVEN Platform: COmprehensive VirtualizEd NF Platform
==========================================================

*Status: Development*

### What is COVEN?

CONVEN is a platform to execute virtualized network function instances. To do that, COVEN implements an innovative Virtualized Network Function latform architecture that natively enables the Network Service Header and Virtualized Network Functions Components. Also, the COVEN platform contains a flexible management agent that provides life cycle and monitoring operations together extensible agents. Extensible agent, in turn, is an innovative concept of personalized management operations implemented directly in the network function and/or network funciton components source code. It is controlled by the management agent through a standart communication channel. In addition, the COVEN platform is generically implemented and can be executed by any virtual machine or container with Python 3 support.<br/>
<br/>

### How was it developed?

COVEN is being developed using standard Python 3 language and other libraries such as:<br/>
1. Bottle (pip3 install bottle)<br/>
2. Requests (pip3 install requests)<br/>
3. Scapy (pip3 install scapy)<br/>
4. NetCat (apt-get install netcat)

Currently, the COVEN platform has support for network functions or network functions components developed with:<br/>
- Python 3 (apt-get install python3)<br/>
- Java Script (apt-get install nodejs)<br/>
- Java (apt-get install default-jdk)<br/>
- Click Modular Router (git clone https://github.com/kohler/click.git)

### Project steps

1. NSH-enabled prototype (OK!!)<br/>
2. VNFC-enabled prototype (OK!!)<br/>
3. Management Agent routines (OK!!)<br/>
4. Example with standard execution script (OK!!)<br/>
5. NSH standard routines development (IN DEVELOPMENT!!)<br/>
6. Migration from Sockets to Shared memory (WAITING)<br/>
7. Prototype migration for low-level language (WAITING)<br/>
8. Packet accelerators integration with VNS (WAITING)<br/>
9. Graphical interface (WAITING)

### Execute example

To execute the project example follow these steps:
1. Execute the platform configuration agent (python3 ConfigurationAgent.py)
2. Execute the example script in Example folder (python3 ExampleScript.py)
3. In the example script execute the "configure"
4. In the example script execute the "start"

After that, the platform and the network function components will be running. To stop the server execute "status", "stop", "reset", "off", and "end". If the the network function components are running management operations can be requested by the commands "list", "check", "request1", "request2", "request3", and "request4".

### Support

Contact us towards git issues requests or by the e-mail vfulber@inf.ufsm.br.

### COVEN Research Group

Vinícius Fülber Garcia (Federal University of Paraná - Brazil)<br/>
Leonardo da Cruz Marcuzzo (Federal University of Santa Maria - Brazil)<br/>
Giovanni Venâncio de Souza (Federal University of Paraná - Brazil)<br/>
Lucas Bondan (Federal University of Porto Alegre - Brazil)<br/>
Jéferson Campos Nobre (University of Vale do Rio dos Sinos - Brazil)<br/>
Alberto Egon Schaeffer-Filho (Federal University of Porto Alegre - Brazil)<br/>
Lisandro Zambenedetti Granville (Federal University of Porto Alegre - Brazil)<br/>
Elias Procópio Duarte Júnior (Federal University of Paraná - Brazil)<br/>
Carlos Raniery Paula dos Santos (Federal University of Santa Maria - Brazil)<br/>

### Publications and Presentations

-> An NSH-Enabled Architecture for Virtualized Network Function Platforms<br/>
V. Fülber Garcia, L. da Cruz Marcuzzo, G. Venâncio de Souza, L. Bondan, J. Campos Nobre, A. Egon Schaeffer-Filho, C. R. Paula dos Santos, L. Zambenedetti Granville, E. P. Duarte Júnior, "An NSH-Enabled Architecture for Virtualized Network Function Platforms", 2019. The 33nd International Conference on Advanced Information Networking and Applications (AINA), Matsue, Japan, 03-2019.

-> Towards a Flexible Architecture for Virtualized Network Function Platforms<br/>
V. Fülber Garcia, L. da Cruz Marcuzzo, E. P. Duarte Júnior, C. R. Paula dos Santos, "Towards a Flexible Architecture for Virtualized Network Function Platforms", 2019. The ACM Latin American Student Workshop on Data Communication Networks (LANCOMM), Gramado, Brazil, 05-2019.

-> On the Design of a Flexible Architecture for Virtualized Network Function Platforms<br/>
V. Fülber Garcia, L. da Cruz Marcuzzo, A. Huff, L. Bondan, J. C. Nobre, A. E. Schaeffer-Filho, C. R. P. dos Santos, L. Z. Granville, E. P. Duarte Junior, "On the Design of a Flexible Architecture for Virtualized Network Function Platforms", 2019. The IEEE Global Communications Conference (GLOBECOM), Waikoloa, USA, 12-2019.
