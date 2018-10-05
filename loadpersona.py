#!/usr/bin/env python3

from xml.etree.ElementTree import (
    ElementTree, Element, SubElement
)

def add_WMS_circulation_persona(
        oclc_personas,

        # mandatory
        institutionId,
        
        # these are not mandatory in the schema but are for WMS Circulation
        barcode,
        borrowerCategory,
        homeBranch,

        # these are optional, but some combinations are required to be
        # used
        idAtSource=None,
        sourceSystem=None,
        oclcUserName=None,
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
        note=None,
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
    

    # either a oclcUserName is defined and idAtSource/sourceSystem are not
    # or oclcUserName is not defined and idAtSource/sourceSystem are defined
    if not (  (oclcUserName!=None and idAtSource==None and sourceSystem==None)
              ^ # exclusive or operator
              (oclcUserName==None and idAtSource!=None and sourceSystem!=None)
            ):
        raise Exception(
            "either a oclcUserName should be defined and "
            "idAtSource/sourceSystem not defined or "
            "oclcUserName not defined and idAtSource/sourcesystem defined")
    
    persona = SubElement(
        oclc_personas, 'persona', attrib={"institutionId": institutionId})
    
    
    if idAtSource!=None:
        correlationInfo = SubElement(persona, 'correlationInfo')
        SubElement(correlationInfo, 'sourceSystem').text=sourceSystem
        SubElement(correlationInfo, 'idAtSource').text=idAtSource


    elif oclcUserName!=None:
        SubElement(persona, 'oclcUserName').text=oclcUserName

    else:
        # checks further up should ensure we process either idAtSource or
        # oclcUserName and throw an Exception if they're both None
        assert(False)
        
    nameInfo = SubElement(persona, 'nameInfo')

    if givenName!=None:
        SubElement(nameInfo, 'givenName').text=givenName
    
    if familyName!=None:
        SubElement(nameInfo, 'familyName').text=familyName

    wmsCircPatronInfo = SubElement(persona, 'wmsCircPatronInfo')

    SubElement(wmsCircPatronInfo, 'barcode').text=barcode
    SubElement(wmsCircPatronInfo, 'borrowerCategory').text=borrowerCategory
    SubElement(wmsCircPatronInfo, 'homeBranch').text=homeBranch

    contactInfo = SubElement(persona, "contactInfo")

    if emailAddresses!=None:
        for i, emailAddress in enumerate(emailAddresses):
            email = SubElement(contactInfo, 'email')
            SubElement(email, 'emailAddress').text=emailAddress
            if i == 0: # first email address is primary
                SubElement(email, 'isPrimary').text='true'
            else:
                SubElement(email, 'isPrimary').text='false'

    if phoneNumbers!=None:
        for phoneNumber in phoneNumbers:
            Phone = SubElement(contactInfo, 'phone')
            SubElement(Phone, 'number').text=phoneNumber


    if streetAddressLine1!=None:
        postalAddress = SubElement(contactInfo, 'postalAddress')
        SubElement(postalAddress, 'streetAddressLine1').text=streetAddressLine1
        if cityOrLocality!=None:
            SubElement(postalAddress, 'cityOrLocality').text=cityOrLocality
        if postalCode!=None:
            SubElement(postalAddress, 'postalCode').text=postalCode
        if country!=None:
            SubElement(postalAddress, 'country').text=country

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
            
        ),

        dict(
            institutionId='1234567',
            barcode='123456789',
            borrowerCategory='P',
            homeBranch='mainBranch',

            oclcUserName='123456789',
            
            givenName='Joe',
            familyName='DiMaggio',

            streetAddressLine1='123 example bay',
            streetAddressLine2='c/o Rosalia',
            cityOrLocality='Martinez',
            stateOrProvince='California',
            country='United States',
            note='Our nation turns its lonely eyes to you'
        ),
        
        
    ) # testPatrons tuple

    for testPatron in testPatrons:
        add_WMS_circulation_persona(oclc_personas, **testPatron)
    ET = ElementTree(oclc_personas)
    ET.write(stdout.buffer)
