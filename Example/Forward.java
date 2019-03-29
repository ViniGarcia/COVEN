import java.util.Arrays;
import java.io.*;
import java.net.*;

public class Forward {

  public static void main(String[] args){
    try{
      Socket fromIR = (new ServerSocket(8008)).accept();
      Socket toIR = new Socket("localhost", 8009);
      byte[] pktData = new byte[1550];
      int pktSize = 0;

      DataOutputStream pktSnd = new DataOutputStream(toIR.getOutputStream());

      while(true){
        pktSize = fromIR.getInputStream().read(pktData);
        System.out.println("OK1!!");
        pktSnd.write(Arrays.copyOfRange(pktData, 0, pktSize));
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
