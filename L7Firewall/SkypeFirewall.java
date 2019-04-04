import javax.xml.bind.DatatypeConverter;
import java.util.Arrays;

import java.io.*;
import java.net.*;

public class SkypeFirewall {

  public void networkFunction(){
    try{
      Socket fromIR = (new ServerSocket(8012)).accept();
      Socket toIR = new Socket("localhost", 8013);
      byte[] pktData = new byte[1514];
      int pktSize = 0;

      DataOutputStream pktSnd = new DataOutputStream(toIR.getOutputStream());

      while(true){
        pktSize = fromIR.getInputStream().read(pktData);

        if (pktSize > 37){
          String ipOptions = Arrays.toString(Arrays.copyOfRange(pktData, 34, 37));
          if (ipOptions.equals("[7, 3, 4]")){
            continue;
          }
        }

        pktSnd.write(Arrays.copyOfRange(pktData, 0, pktSize));
        pktSnd.flush();
      }
    } catch(Exception e){
      System.exit(1);
    }
  }

  public static void main(String[] args){
    SkypeFirewall nfInstance = new SkypeFirewall();
    nfInstance.networkFunction();
  }
}
