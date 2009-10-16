from helixcore.validol.docsgenerator import generate_by_protocol
import webbrowser

def main():
    from helixtariff.validator.validator import protocol
    fname = 'docs.html'
    s = generate_by_protocol(protocol, title='Helixtariff')
    open(fname, 'w').write(s)
    webbrowser.open(fname)

if __name__ == '__main__':
    main()
