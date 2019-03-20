ORDER_KEY = "DE6A6E24F046FB24094E9208C66FEFE7"

CREATE_PAYMENT_RESPONSE = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Body>
        <createResponse ddpXsdVersion="1.3.14" xmlns="http://www.docdatapayments.com/services/paymentservice/1_3/">
            <createSuccess>
                <success code="SUCCESS">Operation successful.</success>
                <key>{}</key>
            </createSuccess>
        </createResponse>
    </S:Body>
</S:Envelope>
""".format(ORDER_KEY)

CANCELLED_PAYMENT_RESPONSE = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Body>
        <cancelResponse ddpXsdVersion="1.3.14" xmlns="http://www.docdatapayments.com/services/paymentservice/1_3/">
            <cancelSuccess>
                <success code="SUCCESS">Operation successful.</success>
                <result>NO_PAYMENTS</result>
            </cancelSuccess>
        </cancelResponse>
    </S:Body>
</S:Envelope>
"""

STATUS_SUCCESS_RESPONSE = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Body>
        <statusResponse ddpXsdVersion="1.3.14" xmlns="http://www.docdatapayments.com/services/paymentservice/1_3/">
            <statusSuccess>
                <success code="SUCCESS">Operation successful.</success>
                <report>
                    <approximateTotals exchangeRateDate="2019-02-10 16:52:52" exchangedTo="EUR">
                        <totalRegistered>299</totalRegistered>
                        <totalShopperPending>0</totalShopperPending>
                        <totalAcquirerPending>0</totalAcquirerPending>
                        <totalAcquirerApproved>299</totalAcquirerApproved>
                        <totalCaptured>299</totalCaptured>
                        <totalRefunded>0</totalRefunded>
                        <totalChargedback>0</totalChargedback>
                        <totalReversed>0</totalReversed>
                    </approximateTotals>
                    <payment>
                        <id>4910079745</id>
                        <paymentMethod>IDEAL</paymentMethod>
                        <authorization>
                            <status>AUTHORIZED</status>
                            <amount currency="EUR">299</amount>
                            <confidenceLevel>ACQUIRER_APPROVED</confidenceLevel>
                            <capture>
                                <status>CAPTURED</status>
                                <amount currency="EUR">299</amount>
                            </capture>
                        </authorization>
                    </payment>
                    <consideredSafe>
                        <value>true</value>
                        <level>SAFE</level>
                        <date>2019-02-10T16:51:43.446+01:00</date>
                        <reason>EXACT_MATCH</reason>
                    </consideredSafe>
                    <apiInformation conversionApplied="false">
                        <originalVersion>1.3</originalVersion>
                    </apiInformation>
                </report>
            </statusSuccess>
        </statusResponse>
    </S:Body>
</S:Envelope>
"""

STATUS_CANCELLED_RESPONSE = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Body>
        <statusResponse xmlns="http://www.docdatapayments.com/services/paymentservice/1_3/">
            <statusSuccess>
                <success code="SUCCESS">Operation successful.</success>
                <report>
                    <approximateTotals exchangeRateDate="2019-02-04 11:11:07" exchangedTo="EUR">
                        <totalRegistered>0</totalRegistered>
                        <totalShopperPending>0</totalShopperPending>
                        <totalAcquirerPending>0</totalAcquirerPending>
                        <totalAcquirerApproved>0</totalAcquirerApproved>
                        <totalCaptured>0</totalCaptured>
                        <totalRefunded>0</totalRefunded>
                        <totalChargedback>0</totalChargedback>
                    </approximateTotals>
                </report>
            </statusSuccess>
        </statusResponse>
    </S:Body>
</S:Envelope>
"""
