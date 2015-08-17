import xml.etree.ElementTree as ET
import requests
import xmltodict
from decimal import *

class Shiptime:
    """Class for interacting with the Shiptime SOAP API
    Only the GetRates service is implemented
    http://sandbox.shiptime.com/api/rating.html#getRates
    """
    def __init__(self, encrypted_password='2A27C164EA2499506FB0CD628AB7B083',
                 encrypted_username='20AE2D8B660FB10B1F4625BB77FCAE3C3EA33586F2DDA2A1EB3349881952AC23', sandbox=True,
                 country=None, notify=False, postal_code=None, residential=False, province=None, attention=None,
                 city=None, company_name=None, phone=None, street_address=None, email=None, instructions=None,
                 street_address2=None):

        """Instance is initialized along with sender information"""
        """Default username/password for the sanbbox server"""

        if sandbox:
            self.url = 'http://sandbox.shiptime.com/api/rating#getRates'
        else:
            self.url = 'http://ship.emergeit.com/api/rating#getRates'

        self.encrypted_password = encrypted_password
        self.encrypted_username = encrypted_username

        if not country:
            raise TypeError('Country code required')
        if not postal_code:
            raise TypeError('Postal code required')
        if not province:
            raise TypeError('Province required')
        if not attention:
            raise TypeError('Attention required')
        if not city:
            raise TypeError('City required')
        if not company_name:
            raise TypeError('Company Name required')
        if not phone:
            raise TypeError('Phone # required')
        if not street_address:
            raise TypeError('Street Address required')

        self.country = country.upper()
        self.notify = notify
        self.postal_code = postal_code.upper()
        self.residential = residential
        self.province = province.upper()
        self.attention = attention
        self.city = city
        self.company_name = company_name
        self.phone = phone
        self.street_address = street_address
        self.street_address2 = street_address2
        self.email = email
        self.instructions = instructions
        self.street_address2 = street_address2

    def get_rates(self, items=None, package_type=None, country=None, notify=False, postal_code=None, residential=False,
                  province=None, attention=None, city=None, company_name=None, phone=None, street_address=None, email=None,
                  instructions=None, street_address2=None, signature=None, saturday_service=None):
        """Requires a list of dictionaries for items_tag (height, length, width, weight in Inches and lbs respectively
        Returns a dictionary of two lists:
        'messages'
        'rates'
        If any messages are 'errors' no rates will be returned.
        """
        if not items:
            raise TypeError('Items code required')
        if not package_type:
            raise TypeError('Package type required')
        if not country:
            raise TypeError('Country code required')
        if not postal_code:
            raise TypeError('Postal code required')
        if not province:
            raise TypeError('Province required')
        if not attention:
            raise TypeError('Attention required')
        if not city:
            raise TypeError('City required')
        if not company_name:
            raise TypeError('Company Name required')
        if not phone:
            raise TypeError('Phone # required')
        if not street_address:
            raise TypeError('Street Address required')

        # Build the XML Request
        root = ET.Element('S:Envelope', attrib={'xmlns:S' : 'http://schemas.xmlsoap.org/soap/envelope/'})
        body = ET.SubElement(root, 'S:Body')
        rates = ET.SubElement(body, 'ns2:getRates', attrib={'xmlns:ns2' : 'http://v1.api.emergeit.com/'})
        key = ET.SubElement(rates, 'Key')
        ET.SubElement(key, 'EncryptedPassword').text = self.encrypted_password
        ET.SubElement(key, 'EncryptedUsername').text = self.encrypted_username
        request = ET.SubElement(rates, 'Request')
        from_tag = ET.SubElement(request, 'From')
        ET.SubElement(from_tag, 'CountryCode').text = self.country
        ET.SubElement(from_tag, 'Notify').text = str(self.notify).lower()
        ET.SubElement(from_tag, 'PostalCode').text = self.postal_code.replace(' ', '')
        ET.SubElement(from_tag, 'Residential').text = str(self.residential).lower()
        ET.SubElement(from_tag, 'Province').text = self.province
        ET.SubElement(from_tag, 'Attention').text = self.attention
        ET.SubElement(from_tag, 'City').text = self.city
        ET.SubElement(from_tag, 'CompanyName').text = self.company_name
        if self.email:
            ET.SubElement(from_tag, 'Email').text = self.email
        if self.instructions:
            ET.SubElement(from_tag, 'Instructions').text = self.instructions
        ET.SubElement(from_tag, 'Phone').text = self.phone
        ET.SubElement(from_tag, 'StreetAddress').text = self.street_address
        if self.street_address2:
            ET.SubElement(from_tag, 'StreetAddress2').text = self.street_address2
        items_tag = ET.SubElement(request, 'ShipmentItems')

        # Attach items
        for item in items:
            item_tag = ET.SubElement(items_tag, 'Item')
            try:
                height = ET.SubElement(item_tag, 'Height')
                ET.SubElement(height, 'UnitsType').text = 'IN'
                ET.SubElement(height, 'Value').text = str(round(Decimal(item['height']) + Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on height')
            try:
                length = ET.SubElement(item_tag, 'Length')
                ET.SubElement(length, 'UnitsType').text = 'IN'
                ET.SubElement(length, 'Value').text = str(round(Decimal(item['length']) + Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on length')
            try:
                width = ET.SubElement(item_tag, 'Width')
                ET.SubElement(width, 'UnitsType').text = 'IN'
                ET.SubElement(width, 'Value').text = str(round(Decimal(item['width']) + Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on width')
            try:
                weight = ET.SubElement(item_tag, 'Weight')
                ET.SubElement(weight, 'UnitsType').text = 'LB'
                ET.SubElement(weight, 'Value').text = str(round(Decimal(item['weight']) + Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on weight')

        ET.SubElement(request, 'PackageType').text = package_type.upper()
        if signature or saturday_service:
            service_options = ET.SubElement(request, 'ServiceOptions')
            if signature:
                ET.SubElement(service_options, 'Signature').text = signature
            if saturday_service:
                ET.SubElement(service_options, 'SaturdayService').text = saturday_service

        to_tag = ET.SubElement(request, "To")
        ET.SubElement(to_tag, 'CountryCode').text = country
        ET.SubElement(to_tag, 'Notify').text = str(notify).lower()
        ET.SubElement(to_tag, 'PostalCode').text = postal_code.replace(' ', '')
        ET.SubElement(to_tag, 'Residential').text = str(residential).lower()
        ET.SubElement(to_tag, 'Province').text = province
        ET.SubElement(to_tag, 'Attention').text = attention
        ET.SubElement(to_tag, 'City').text = city
        ET.SubElement(to_tag, 'CompanyName').text = company_name
        if email:
            ET.SubElement(to_tag, 'Email').text = email
        if instructions:
            ET.SubElement(to_tag, 'Instructions').text = instructions
        ET.SubElement(to_tag, 'Phone').text = phone
        ET.SubElement(to_tag, 'StreetAddress').text = street_address
        if street_address2:
            ET.SubElement(to_tag, 'StreetAddress2').text = street_address2

        # Complete xml string
        xml = ET.tostring(root)

        # Make the request
        response = requests.post(self.url, data=xml)
        #print(response.text)

        # Ignore namespace information
        namespaces = {'http://schemas.xmlsoap.org/soap/envelope/' : None,
                      "http://v1.api.emergeit.com/" : None}

        # Parse the response into a dictionary
        response_dict = xmltodict.parse(response.text, process_namespaces=True, namespaces=namespaces)

        # Dictionary to hold the processed results
        shiptime_response = {'messages' : [], 'rates' : []}

        # Extract messages and process
        messages = response_dict['Envelope']['Body']['getRatesResponse']['Response']['Messages']

        if messages:
            # Because of the way the xml is parsed need to treat singleton messages differently
            # Essentially a single message is a dict inside a dict, whereas multiple messages are dicts inside lists
            # inside dicts
            if type(messages['Message']) != type([]):
                shiptime_response['messages'].append({'severity' : messages['Message']['Severity'],
                                                      'text' : messages['Message']['Text']})
            else:
                for message in messages['Message']:
                    print(message)
                    shiptime_response['messages'].append({'severity' : message['Severity'], 'text' : message['Text']})

            # Bail out if an error message is returned
            for message in shiptime_response['messages']:
                if message['severity'] == 'ERROR':
                    return shiptime_response

        # Extract rates and process
        available_rates = response_dict['Envelope']['Body']['getRatesResponse']['Response']['AvailableRates']

        if available_rates:
            # Same reasoning per the above
            if type(available_rates['Rate']) != type([]):
                shiptime_response['rates'].append({'service_name' : available_rates['Rate']['ServiceName'],
                                        'total_after_tax' : Decimal(available_rates['Rate']['TotalCharge']['Amount'])/100,
                                        'transit_time' : int(available_rates['Rate']['TransitDays'])})

            else:
                for rate in available_rates['Rate']:
                    shiptime_response['rates'].append({'service_name' : rate['ServiceName'],
                                            'total_after_tax' : Decimal(rate['TotalCharge']['Amount'])/100,
                                            'transit_time' : int(rate['TransitDays'])})

        return shiptime_response


# Copied values from the sample request for testing
# http://sandbox.shiptime.com/api/SampleGetRatesRequest.xml
if __name__ == '__main__':

    shipper = Shiptime(country='CA', postal_code='M9A4M5', province='ON', attention='Attention name', city='Etobicoke',
                       company_name='Origin Company', phone='123-456-7890', street_address='Address 1')


    response = shipper.get_rates(items=[{'height' : 3, 'length' : 5, 'width' : 4, 'weight' : 2}], package_type='PACKAGE',
                                 country='CA', postal_code='M2M2M2', residential=False, province='ON',
                                 attention='Attention name', city='North York', company_name='Test Company', phone='123-456-7890',
                                 street_address='Address 1')

    for message in response['messages']:
        print(message)

    for rate in response['rates']:
        print(rate)
