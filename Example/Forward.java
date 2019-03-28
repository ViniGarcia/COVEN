import java.io.*;
import java.net.*;

public class Forward {

  public static void main(String[] args){
    try{
      Socket fromIR = new ServerSocket(8008).accept();
      Socket toIR = new Socket("localhost", 8009);
      String pkt = null;

      DataInputStream pktRcv = new DataInputStream(fromIR.getInputStream());
      DataOutputStream pktSnd = new DataOutputStream(toIR.getOutputStream());

      while(true){
        pkt = (String) pktRcv.readUTF();
        pktSnd.writeUTF(pkt);
        pktSnd.flush();
      }

      // fromIR.close();
      // toIR.close();
      // pktRcv.close();
      // pktSnd.close();

    } catch(Exception e){
      System.exit(1);
    }
  }

}
