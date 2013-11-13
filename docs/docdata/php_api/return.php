<pre>
    <?php

        $key = $_GET['key'];

        $url = "http://test.tripledeal.com/ps/services/paymentservice/1_0?wsdl";

        $client = new SoapClient( $url );

        //var_dump($client->__getFunctions());

        $parameters = array();

        $parameters['version'] = "1.0";

        //  merchant
        //$parameters['merchant']['name'] = $_POST['merchantname'];
        //$parameters['merchant']['password'] = $_POST['merchantpassword'];
        $parameters['merchant']['name'] = 'phptest';
        $parameters['merchant']['password'] = 'fdUDhGBT';


        $parameters['paymentOrderKey'] = $key;

        //  dorequest
        echo "<h2>Status</h2>";

        $response = $client->status( $parameters );

        if( isset( $response->statusSuccess->success ) ) {
            print_r($response->statusSuccess->report);
        } else {
            print_r( $response->statusError );
        }
    ?>
</pre>
