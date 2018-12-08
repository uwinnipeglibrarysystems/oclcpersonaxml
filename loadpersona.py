#!/usr/bin/env python3
# two functions here can be imported to python3 programs as well, not sure
# about __main__ section

from datetime import date, datetime

from xml.etree.ElementTree import (
    ElementTree, Element, SubElement
)

MAX_GIVEN_NAME, MAX_FAMILY_NAME, MAX_TELEPHONE_NUM, MAX_POSTAL_CODE = (
    50, 50, 50, 20)

def process_address(persona,
                    streetAddressLine1,
                    streetAddressLine2=None,
                    cityOrLocality=None,
                    stateOrProvince=None,
                    postalCode=None,
                    country=None):
    contactInfo_address = SubElement(persona, "contactInfo")
    postalAddress = SubElement(contactInfo_address, 'postalAddress')
    SubElement(postalAddress, 'streetAddressLine1').text=streetAddressLine1
    if streetAddressLine2!=None:
        SubElement(postalAddress, 'streetAddressLine2').text=streetAddressLine2
    if cityOrLocality!=None:
        SubElement(postalAddress, 'cityOrLocality').text=cityOrLocality
    if stateOrProvince!=None:
        SubElement(postalAddress, 'stateOrProvince').text=stateOrProvince
    if postalCode!=None:
        SubElement(postalAddress, 'postalCode').text=postalCode
    if country!=None:
        SubElement(postalAddress, 'country').text=country

def add_WMS_circulation_persona(
        oclc_personas,

        # mandatory
        institutionId,
        
        # these are not mandatory in the schema but are for WMS Circulation
        barcode,
        borrowerCategory,
        homeBranch,

        # optional, but must use idAtSource and sourceSystem together
        idAtSource=None,
        sourceSystem=None,
        oclcUserName=None,

        # at lease one of these must be used
        givenName=None,
        familyName=None,

        # a list of email addresses, the first will be considered primary
        emailAddresses=None,
        
        phoneNumbers=None,
        streetAddressLine1=None,
        streetAddressLine2=None,
        cityOrLocality=None,
        stateOrProvince=None,
        postalCode=None,
        country=None,
        additionalAddresses=None,
        note=None,
        expiry=None,
        **kargs
):
    if not (givenName!=None or familyName!=None):
        raise Exception("at least one of givename or familyName must be used")

    if (emailAddresses==None and phoneNumbers==None and
        streetAddressLine1==None):
        raise Exception("at least an email address, phone number, or "
                        "street address should be included")

    if not  ( (isinstance(emailAddresses, list) and len(emailAddresses)>0 )
              or
              (isinstance(phoneNumbers, list) and len(phoneNumbers)>0 )
              or
              streetAddressLine1!=None ):
        raise Exception("at least one email address (list length 1), "
                        "one phone number (list length 1) "
                        "or one street address must be included"
                        )

    if postalCode != None and len(postalCode)>MAX_POSTAL_CODE:
        raise Exception("Postal code longer than %d characters '%s'" % (
                        MAX_POSTAL_CODE, postalCode ) )

    if givenName != None and len(givenName)>MAX_GIVEN_NAME:
        raise Exception("Given name longer than %d characters '%s'" % (
                        MAX_GIVEN_NAME, givenName ) )

    if familyName != None and len(familyName)>MAX_FAMILY_NAME:
        raise Exception("Family name longer than %d characters '%s'" % (
                        MAX_FAMILY_NAME, familyName) )

    if phoneNumbers !=None and any( len(num)>MAX_TELEPHONE_NUM
                                   for num in phoneNumbers ):
        raise Exception("Phone number longer than %d characters '%s'" % (
                        MAX_TELEPHONE_NUM, ' '.join(phoneNumbers) ) )
    
    persona = SubElement(
        oclc_personas, 'persona', attrib={"institutionId": institutionId})
    
    
    if idAtSource!=None:
        if sourceSystem==None:
            raise Exception(
                "sourceSystem must be defined when using idAtSource")
        correlationInfo = SubElement(persona, 'correlationInfo')
        SubElement(correlationInfo, 'sourceSystem').text=sourceSystem
        SubElement(correlationInfo, 'idAtSource').text=idAtSource


    if oclcUserName!=None:
        SubElement(persona, 'oclcUserName').text=oclcUserName

    if expiry!=None:
        if isinstance(expiry, datetime):
            pass
        elif isinstance(expiry, date):
            # convert to a datetime with midnight as the time of day
            expiry = datetime.combine(expiry, datetime.min.time())
        else:
            raise Exception("expiry must be a date or datetime")
        SubElement(persona, 'oclcExpirationDate').text=expiry.isoformat()
        
    nameInfo = SubElement(persona, 'nameInfo')

    if givenName!=None:
        SubElement(nameInfo, 'givenName').text=givenName
    
    if familyName!=None:
        SubElement(nameInfo, 'familyName').text=familyName

    wmsCircPatronInfo = SubElement(persona, 'wmsCircPatronInfo')

    SubElement(wmsCircPatronInfo, 'barcode').text=barcode
    SubElement(wmsCircPatronInfo, 'borrowerCategory').text=borrowerCategory
    SubElement(wmsCircPatronInfo, 'homeBranch').text=homeBranch

    if emailAddresses!=None:
        for i, emailAddress in enumerate(emailAddresses):
            contactInfo_email = SubElement(persona, "contactInfo")
            email = SubElement(contactInfo_email, 'email')
            SubElement(email, 'emailAddress').text=emailAddress
            if i == 0: # first email address is primary
                SubElement(email, 'isPrimary').text='true'
            else:
                SubElement(email, 'isPrimary').text='false'

    if phoneNumbers!=None:
        for phoneNumber in phoneNumbers:
            contactInfo_phone = SubElement(persona, "contactInfo")
            Phone = SubElement(contactInfo_phone, 'phone')
            SubElement(Phone, 'number').text=phoneNumber


    if streetAddressLine1!=None:
        process_address(
            persona,
            streetAddressLine1,
            streetAddressLine2,
            cityOrLocality,
            stateOrProvince,
            postalCode,
            country)

    if None!=additionalAddresses:
        for addr in additionalAddresses:
            process_address(persona, **addr)

            
    if note!=None:
        note_element = SubElement(persona, 'note')
        SubElement(note_element, 'text').text=note

def create_personas_element():
    return Element(
        'oclcPersonas',
        attrib={'xmlns':"http://worldcat.org/xmlschemas/IDMPersonas-2.2",
                'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation':
                "http://worldcat.org/xmlschemas/IDMPersonas-2.2 "
                "IDMPersonas-2.2.xsd"
        } # attrib
    ) # Element

if __name__ == "__main__":
    from sys import stdout

    oclc_personas = create_personas_element()
    testPatrons = (
        dict(
            institutionId='1234567',
            barcode='123456789',
            borrowerCategory='P',
            homeBranch='mainBranch',

            idAtSource='torvalds-l',
            sourceSystem='LDAP',
        
            givenName='Linus',
            familyName='Torvalds',

            emailAddresses=['linus@example.tld'],

            note='Famous, treat with kid gloves, penguins bite'
        ),

        dict(
            institutionId='1234567',
            barcode='123456789',
            borrowerCategory='P',
            homeBranch='mainBranch',

            idAtSource='john-c',
            sourceSystem='LDAP',
        
            givenName='John',

            phoneNumbers=['+12042222222', '+999-800-PIZZA-ZA'],

            note='Great pizza for a great price'
        ),

        dict(
            institutionId='1234567',
            barcode='123456789',
            borrowerCategory='P',
            homeBranch='mainBranch',

            oclcUserName='123456789',
            
            familyName='Ricardo',

            emailAddresses=['ricardo@example.tld', 'ric@new.tld'],
            phoneNumbers=['+999-800-12345-67'],

            streetAddressLine1='666 example st.',
            cityOrLocality='Beverly Hills',
            stateOrProvince='California',
            postalCode='90210',
            expiry=datetime(2018,1,1,13,0)
        ),

        dict(
            institutionId='1234567',
            barcode='123456789',
            borrowerCategory='P',
            homeBranch='mainBranch',

            givenName='Joe',
            familyName='DiMaggio',

            streetAddressLine1='123 example bay',
            streetAddressLine2='c/o Rosalia',
            cityOrLocality='Martinez',
            stateOrProvince='California',
            country='United States',
            note='Our nation turns its lonely eyes to you',
            expiry=date(2018,1,1)
        ),
        
        
    ) # testPatrons tuple

    for testPatron in testPatrons:
        add_WMS_circulation_persona(oclc_personas, **testPatron)
    ET = ElementTree(oclc_personas)
    ET.write(stdout.buffer)
