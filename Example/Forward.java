import java.util.Arrays;
import java.io.*;
import java.net.*;

public class Forward implements Runnable {

  int processedPackets;

  public Forward(){
    this.processedPackets = 0;
  }

  public void networkFunction(){
    try{
      Socket fromIR = (new ServerSocket(8008)).accept();
      Socket toIR = new Socket("localhost", 8009);
      byte[] pktData = new byte[1514];
      int pktSize = 0;

      DataOutputStream pktSnd = new DataOutputStream(toIR.getOutputStream());

      while(true){
        pktSize = fromIR.getInputStream().read(pktData);
        this.processedPackets += 1;
        System.out.println("OK1!! " + pktSize);
        pktSnd.write(Arrays.copyOfRange(pktData, 0, pktSize));
        pktSnd.flush();
      }
    } catch(Exception e){
      System.exit(1);
    }
  }

  public void run(){

    try{
      ServerSocket clientConnection = new ServerSocket(8020);

      byte[] messageBytes = new byte[1500]; //Maximum request size
      int quantityBytes = 0;
      String stringBytes = null;

      while(true){
        Socket clientSocket = clientConnection.accept();

        DataInputStream clientInput = new DataInputStream(clientSocket.getInputStream());
        quantityBytes = clientInput.read(messageBytes);
        stringBytes = new String(messageBytes, 0, quantityBytes);

        if (stringBytes.equals("PP")){
          PrintWriter clientOutput = new PrintWriter(clientSocket.getOutputStream(), true);
          clientOutput.println(this.processedPackets);
        } else{
          PrintWriter clientOutput = new PrintWriter(clientSocket.getOutputStream(), true);
          clientOutput.println("INVALID REQUEST!!");
        }

        clientSocket.close();
      }
    } catch (Exception e) {
      System.out.println("EXTENDED AGENT STOPPED!!");
    }

  }

  public static void main(String[] args){
    Forward nfInstance = new Forward();
    Thread extendAgent = new Thread(nfInstance);

    extendAgent.start();
    nfInstance.networkFunction();
  }
}
