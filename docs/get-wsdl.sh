#!/bin/sh

for version in 1_0 1_1 1_2
do
  curl "https://test.docdatapayments.com/ps/services/paymentservice/$version?wsdl" > wsdl-$version.wsdl
  curl "https://test.docdatapayments.com/ps/services/paymentservice/$version?xsd=1" > xsd1-$version.xsd
  curl "https://test.docdatapayments.com/ps/services/paymentservice/$version?xsd=2" > xsd2-$version.xsd
done
