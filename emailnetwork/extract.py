from email.utils import getaddresses
from mailbox import mbox

from mailbox import mboxMessage


from emailnetwork.utils import clean_subject, clean_body
from emailnetwork.emails import EmailAddress, EmailMeta, EmailBody

def extract_meta(email):

    recs = email.get_all('To', []) + email.get_all('Resent-To', [])
    ccs = email.get_all('Cc', []) + email.get_all('Resent-Cc', [])
    
    return EmailMeta(
        sender=EmailAddress(getaddresses(email.get_all('From'))[0]),
        recipients=[EmailAddress(rec) for rec in getaddresses(recs)],
        cc=[EmailAddress(cc) for cc in getaddresses(ccs)],
        subject=clean_subject(email['Subject']) or None,
        date=email['Date']
    )

def extract_body(email):

    return EmailBody(
        subject = clean_subject(email['Subject']) or None,
        body = clean_body(email)
    )

class MBoxReader(object):
    """ A class that extends python's `mailbox` module to provide additional 
    functionalities such as length, date filtering and parsing. A key component of 
    many `emailnetwork`'s operations.

    Usage:
        reader = MboxReader('path-to-mbox.mbox')

    Args:
        object ([type]): Instantiate this class by specifying a path to an `.mbox` object
    """
    
    def __init__(self, path) -> None:
        super().__init__()
        self.path = path
        self.mbox = mbox(path)

    def __iter__(self):
        for msg in self.mbox:
            yield msg

    def __len__(self):
        return self.count()

    def count(self):
        """
        Count the number of emails in the mbox instance.
        Helper function to implement __len__ 
        """
        return self.mbox.keys()[-1]+1 
        # return len(self.mbox.keys())

    def extract(self):
        """
        Extract the meta data from the Mbox instance
        """
        for email in self:
            try:
                emailmeta = extract_meta(email)
                if emailmeta is not None:
                    yield emailmeta

            except Exception as e:
                print(e)
                continue

    
    def filter_by_date(self, operator:str, datestring:str):
        if operator not in ['>=', '==', '<=']:
            raise ValueError("Please use one of ['>=', '==', '<=']")
        
        val = []
        for email in self.mbox:
            emailmeta = extract_meta(email)
            if operator == '>=':
                if emailmeta >= datestring:
                    val.append(emailmeta)
            elif operator == '==':
                if emailmeta == datestring:
                    val.append(emailmeta)
            elif operator == '<=':
                if emailmeta <= datestring:
                    val.append(emailmeta)
        return val



if __name__ == '__main__':
    # reader = MBoxReader('/Users/samuel/Footprints/samuel-supertype.mbox')
    import os
    MBOX_PATH = f'{os.path.dirname(__file__)}/tests/test.mbox'
    reader = MBoxReader(MBOX_PATH)
    print(f'{len(reader)} emails in the sample mbox.')
    # email = reader.mbox[646]
    email = reader.mbox[0]
    emailmsg = extract_meta(email)
    # print(reader)
    # print(type(email))
    # print(email.is_multipart())
    emailbody = extract_body(email)
    print(mboxMessage(email._payload[0]).keys())
    
    thisyearmails = reader.filter_by_date(">=", "2021-01-05")
    # print(emailmsg.recipients)
    # print(emailmsg.recipients[0].domain)
    emails = reader.extract()
    #[email.origin_domain for email in emails]
    