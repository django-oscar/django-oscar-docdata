<pre>
    <h2>Post</h2>
<?php
    //  Example by www.individualae.nl
    //  info@individualae.nl
    //  +31(0)20-6982047

    print_r($_POST);

    $url        = "http://test.tripledeal.com/ps/services/paymentservice/1_0?wsdl";
    $base_url   = 'http://localhost/docdatapayment/';                               // only required for example

    $client = new SoapClient( $url );

    $parameters = array();

    $parameters['version'] = "1.0";

    //  merchant information
    $parameters['merchant']['name'] = $_POST['merchantname'];
    $parameters['merchant']['password'] = $_POST['merchantpassword'];

    $parameters['paymentPreferences']['profile'] = 'standard';
    $parameters['paymentPreferences']['numberOfDaysToPay'] = '14';

    //  order reference
    $parameters['merchantOrderReference'] = $_POST['merchantOrderReference'];       // order reference must be unique

    $parameters['totalGrossAmount'] = array(
                            '_' => '2000',
                            'currency' => 'EUR');

    //  shopper information
    $parameters['shopper']['id'] = $_POST['shopperid'];
    $parameters['shopper']['name']['first'] = $_POST['shoppernamefirst'];
    $parameters['shopper']['name']['last'] = $_POST['shoppernamelast'];
    $parameters['shopper']['email'] = $_POST['shopperemail'];
    $parameters['shopper']['language']['code'] = $_POST['shopperlanguagecode'];
    $parameters['shopper']['gender'] = $_POST['shoppergender'];
    $parameters['shopper']['dateOfBirth'] = $_POST['shopperdateOfBirth'];
    $parameters['shopper']['phoneNumber'] = $_POST['shopperphoneNumber'];
    $parameters['shopper']['mobilePhoneNumber'] = $_POST['shoppermobilePhoneNumber'];

    //  billing to information
    $parameters['billTo']['name']['first'] = $_POST['shoppernamefirst'];
    $parameters['billTo']['name']['last'] = $_POST['shoppernamelast'];
    $parameters['billTo']['name']['initials'] = $_POST['shoppernameinitials'];
    $parameters['billTo']['address']['street'] = $_POST['street'];
    $parameters['billTo']['address']['houseNumber'] = $_POST['houseNumber'];
    $parameters['billTo']['address']['postalCode'] = $_POST['postalCode'];
    $parameters['billTo']['address']['city'] = $_POST['city'];
    $parameters['billTo']['address']['country']['code'] = $_POST['country'];

    //  shipto information is required to set when using invoice
    //  invoice is required for using lineitems
    $parameters['invoice']['shipTo']['name']['first'] = $_POST['shoppernamefirst'];
    $parameters['invoice']['shipTo']['name']['last'] = $_POST['shoppernamelast'];
    $parameters['invoice']['shipTo']['address']['street'] = $_POST['street'];
    $parameters['invoice']['shipTo']['address']['houseNumber'] = $_POST['houseNumber'];
    $parameters['invoice']['shipTo']['address']['postalCode'] = $_POST['postalCode'];
    $parameters['invoice']['shipTo']['address']['city'] = $_POST['city'];
    $parameters['invoice']['shipTo']['address']['country']['code'] = $_POST['country'];

    // invoice information required when using lineitems
    $parameters['invoice']['additionalDescription']     = "Additional information";
    $parameters['invoice']['totalNetAmount']            = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['totalVatAmount']            =  array(
                         '_' => '190',
                         'currency' => 'EUR',
                         'rate' => '19');

    //  lineitem - 1
    $parameters['invoice']['item'][0]['number'] = '12345';
    $parameters['invoice']['item'][0]['name'] = 'Test product';
    $parameters['invoice']['item'][0]['code'] = '12345';
    $parameters['invoice']['item'][0]['quantity'] = array(
                         '_' => '1',
                         'unitOfMeasure' => 'PCS');

    $parameters['invoice']['item'][0]['description'] = 'Dit is een test product';
    $parameters['invoice']['item'][0]['netAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][0]['grossAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][0]['vat'] = array(
                            'rate' => '19',
                                'amount' => array(
                                    '_' => '190',
                                    'currency' => 'EUR')
                                );
    $parameters['invoice']['item'][0]['totalNetAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][0]['totalGrossAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][0]['totalVat'] = array(
                            'rate' => '19',
                                'amount' => array(
                                    '_' => '119',
                                    'currency' => 'EUR') );
    //  lineitem - 2
    $parameters['invoice']['item'][1]['number'] = '789';
    $parameters['invoice']['item'][1]['name'] = 'Test product 2';
    $parameters['invoice']['item'][1]['code'] = '789';
    $parameters['invoice']['item'][1]['quantity'] = array(
                         '_' => '1',
                         'unitOfMeasure' => 'PCS');

    $parameters['invoice']['item'][1]['description'] = 'Dit is een test product 2';
    $parameters['invoice']['item'][1]['netAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][1]['grossAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][1]['vat'] = array(
                            'rate' => '19',
                                'amount' => array(
                                    '_' => '190',
                                    'currency' => 'EUR')
                                );
    $parameters['invoice']['item'][1]['totalNetAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][1]['totalGrossAmount'] = array(
                         '_' => '1000',
                         'currency' => 'EUR');
    $parameters['invoice']['item'][1]['totalVat'] = array(
                            'rate' => '19',
                                'amount' => array(
                                    '_' => '119',
                                    'currency' => 'EUR') );

    //  dorequest
    echo "<h2>Create</h2>";

    $response = $client->create( $parameters );

    $parameters['paymentOrderKey'] = '';

    if( isset( $response->createSuccess->success ) ) {
        echo "Order created successfull with key " . $response->createSuccess->key;
        $parameters['paymentOrderKey'] = $response->createSuccess->key;
    } else {
        print_r( $response->createError );
    }

    // create redirect url
    $url = array();
    $url['payment_cluster_key']     = $parameters['paymentOrderKey'];
    $url['merchant_name']           = $parameters['merchant']['name'];
    $url['return_url_success']      = $base_url . 'return.php?key='. $url['payment_cluster_key'];
    $url['return_url_pending']      = $base_url . 'return.php?key='. $url['payment_cluster_key'];
    $url['return_url_canceled']     = $base_url . 'return.php?key='. $url['payment_cluster_key'];
    $url['return_url_error']        = $base_url  .'return.php?key='. $url['payment_cluster_key'];
    $url['locale']                  = '';
    $redirecturl = 'https://test.docdatapayments.com/ps/menu?';

    $counter = 0;
    foreach( $url as $key => $item ) {
        $seperator = "&";

        if($counter == 0 ) $seperator = "";
        $redirecturl .= $seperator . $key . "=" . $item;

        $counter++;
    }

?>
</pre>
<?php
    echo '<a href="'. $redirecturl .'">' . $redirecturl . '</a>';
?>
