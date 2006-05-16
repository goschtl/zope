import smtplib, sys
from email.MIMEText import MIMEText

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    [data] = args

    server = smtplib.SMTP('smtp.zope.com')
    from_addr = 'legal@zope.org'
    invitation = open('invitation.txt').read()

    for record in open(data):
        login, first, last, email = record.strip().split('\t')
        if first == '(unknown)':
            if last == '(unknown)':
                name = ''
            else:
                name = last
        else:
            if last == '(unknown)':
                name = first
            else:
                name = first + ' ' + last

        if name.strip():
            to = '"%s" <%s>' % (name, email)
        else:
            to = '<%s>' % email

        msg = MIMEText(invitation)
        msg['Subject'] = 'Test message, please ignore'
        msg['From'] = 'Zope Foundation <legal@zope.org>'
        msg['Cc'] = 'Zope Foundation <legal@zope.org>'
        msg['To'] = to
        server.connect()
        server.sendmail(from_addr, [email, from_addr], msg.as_string())
        server.close()

if __name__ == '__main__':
    main()
