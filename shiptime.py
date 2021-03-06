import xml.etree.ElementTree as ET
import logging
import re
from decimal import *
from operator import itemgetter

import requests
import xmltodict


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class Shiptime:
    """Class for interacting with the Shiptime SOAP API
    Only the GetRates service is implemented
    http://sandbox.shiptime.com/api/rating.html#getRates
    """
    def __init__(self, encrypted_password='2A27C164EA2499506FB0CD628AB7B083',
                 encrypted_username='20AE2D8B660FB10B1F4625BB77FCAE3C3EA33586F2DDA2A1EB3349881952AC23',
                 sandbox=True, street_address2=None, notify=False, instructions=None,
                 residential=False, email=None, *, country, postal_code, province,
                 attention, city, company_name, phone, street_address):

        """Instance is initialized along with sender information"""
        """Default username/password for the sanbbox server"""

        if sandbox:
            self.url = 'http://sandbox.shiptime.com/api/rating#getRates'
        else:
            self.url = 'http://ship.emergeit.com/api/rating#getRates'

        self.encrypted_password = encrypted_password
        self.encrypted_username = encrypted_username

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

    def get_rates(self, residential=False, notify=False, email=None, instructions=None,
                  street_address2=None, signature=None, saturday_service=None,
                  retry=False, *, items, package_type, country, postal_code,
                  province, attention, city, company_name, phone, street_address):
        """Requires a list of dictionaries for items_tag
        (height, length, width, weight in Inches and lbs respectively
        Returns a dictionary of two lists:
        'messages'
        'rates' - sorted ascending by total_before_tax
        If any messages are 'errors' no rates will be returned.
        """
        if not items:
            raise TypeError('Items dictionary required')

        # Build the XML Request
        root = ET.Element('S:Envelope',
                          attrib={'xmlns:S': 'http://schemas.xmlsoap.org/soap/envelope/'})
        body = ET.SubElement(root, 'S:Body')
        rates = ET.SubElement(body, 'ns2:getRates',
                              attrib={'xmlns:ns2': 'http://v1.api.emergeit.com/'})
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
                ET.SubElement(height, 'Value').text = str(round(Decimal(item['height']) +
                                                                Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on height')
            try:
                length = ET.SubElement(item_tag, 'Length')
                ET.SubElement(length, 'UnitsType').text = 'IN'
                ET.SubElement(length, 'Value').text = str(round(Decimal(item['length']) +
                                                                Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on length')
            try:
                width = ET.SubElement(item_tag, 'Width')
                ET.SubElement(width, 'UnitsType').text = 'IN'
                ET.SubElement(width, 'Value').text = str(round(Decimal(item['width']) +
                                                               Decimal(0.5), 0))
            except KeyError:
                raise KeyError('Key Error on width')
            try:
                weight = ET.SubElement(item_tag, 'Weight')
                ET.SubElement(weight, 'UnitsType').text = 'LB'
                ET.SubElement(weight, 'Value').text = str(round(Decimal(item['weight']) +
                                                                Decimal(0.5), 0))
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
        print('Right before shiptime request')
        response = requests.post(self.url, data=xml, timeout=7)
        print('Right after shiptime request')
        response.raise_for_status()

        # Ignore namespace information
        namespaces = {'http://schemas.xmlsoap.org/soap/envelope/': None,
                      "http://v1.api.emergeit.com/": None}

        # Parse the response into a dictionary
        response_dict = xmltodict.parse(response.text, process_namespaces=True,
                                        namespaces=namespaces)

        # Dictionary to hold the processed results
        shiptime_response = {'messages': [], 'rates': []}

        # Extract messages and process
        messages = response_dict['Envelope']['Body']['getRatesResponse']['Response']['Messages']

        if messages:
            # Because of the way the xml is parsed need to treat singleton messages
            # differently Essentially a single message is a dict inside a dict,
            # whereas multiple messages are dicts inside lists # inside dicts
            if not isinstance(messages['Message'], list):
                shiptime_response['messages'].\
                    append({'severity': messages['Message']['Severity'],
                            'text': messages['Message']['Text']})
            else:
                for message in messages['Message']:
                    print(message)
                    shiptime_response['messages'].\
                        append({'severity': message['Severity'], 'text': message['Text']})

        # Do a check to see if there was an error about postal codes.
        # If there was (and this is not a retry), redo the request with the suggested city
        if not retry:
            for message in shiptime_response['messages']:
                if message['text'].startswith('Postal Code'):

                    corrected_city = re.findall(r"only valid for ([^,]*)", message['text'])[0]
                    print('Retrying shiptime API. Replacing {} with {}'.format(city, corrected_city))

                    return self.\
                        get_rates(residential=residential, notify=notify, email=email,
                                  instructions=instructions,
                                  street_address2=street_address2, signature=signature,
                                  saturday_service=saturday_service, retry=True,
                                  items=items, package_type=package_type, country=country,
                                  postal_code=postal_code, province=province,
                                  attention=attention, city=corrected_city,
                                  company_name=company_name, phone=phone,
                                  street_address=street_address)
        else:
            # Add a message that the city was modified (only reason we are here is this is a 'retry'
            shiptime_response['messages'].\
                append({'severity': 'Warning',
                        'text': 'City was changed to {}.'.format(city)})

        # Bail out if an error message is returned
        for message in shiptime_response['messages']:
            if message['severity'] == 'ERROR':
                return shiptime_response

        # Extract rates and process
        available_rates = response_dict['Envelope']['Body']['getRatesResponse']['Response']['AvailableRates']

        if available_rates:
            # Same reasoning per the above
            if not isinstance(available_rates['Rate'], list):
                shiptime_response['rates'].\
                    append({'service_name': available_rates['Rate']['ServiceName'],
                            'total_before_tax': Decimal(available_rates['Rate']['TotalBeforeTaxes']['Amount'])/100,
                            'transit_time': int(available_rates['Rate']['TransitDays'])})

            else:
                for rate in available_rates['Rate']:
                    shiptime_response['rates'].\
                        append({'service_name': rate['ServiceName'],
                                'total_before_tax': Decimal(rate['TotalBeforeTaxes']['Amount'])/100,
                                'transit_time': int(rate['TransitDays'])})

            # Sort the rates ascending
            shiptime_response['rates'].sort(key=itemgetter('total_before_tax'))

        return shiptime_response


# Copied values from the sample request for testing
# http://sandbox.shiptime.com/api/SampleGetRatesRequest.xml
if __name__ == '__main__':

    shipper = Shiptime(country='CA', postal_code='M9A4M5', province='ON',
                       attention='Attention name', city='Etobicoke',
                       company_name='Origin Company', phone='123-456-7890',
                       street_address='Address 1')

    response = shipper.get_rates(items=[{'height': 3, 'length': 5, 'width': 4, 'weight': 2},
                                        {'height': 3, 'length': 5, 'width': 4, 'weight': 2}],
                                 package_type='PACKAGE', country='CA',
                                 postal_code='M2M2M2', residential=False, province='ON',
                                 attention='Attention name', city='North York',
                                 company_name='Test Company', phone='123-456-7890',
                                 street_address='Address 1')

    for message in response['messages']:
        print(message)

    for rate in response['rates']:
        print(rate)
