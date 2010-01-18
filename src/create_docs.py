#!/usr/bin/python
from helixcore.validol.docsgenerator import generate_htmldoc_by_protocol,\
    DocItem, docstring_formatter, sorted_hash_items
from helixcore.validol.validol import Optional
import webbrowser

def format_top_args(data, prefix='        '):
    lines = [prefix + 'self,']
    hash_items = data.validators[0].items()
    for i, (key, value) in enumerate(sorted_hash_items(hash_items)): #@UnusedVariable
        if isinstance(key, Optional):
            lines.append(prefix + '%s=None,' % key.data)
        else:
            lines.append(prefix + '%s,' % key)
    return '\n'.join(lines)

def format_response(c):
    items = c.scheme.validators[0].validators[0]
    items.pop('status', None)
    return docstring_formatter.format(items)

def generate_accessors_by_protocol(protocol):
    protocol = map(DocItem, protocol)
    requests =  [c for c in protocol if c.io_type == 'request']
    responses = dict((c.cleaned_name, c) for c in protocol if c.io_type == 'response')
    bits = []
    for c in requests:
        response_descr = ''.join(
            '        %s\n' % line
            for line in ('@return: ' + format_response(responses[c.cleaned_name])).split('\n')
            if line.strip()
        )
        action_descr = c.description.strip() + '\n'
        if response_descr.strip() == '@return: {}':
            bits.append(
                '''    def %(action)s(\n'''
                '''%(top_args)s\n'''
                '''    ):\n'''
                '''        """\n'''
                '''        %(action_descr)s'''
                '''        @raise HelixApiError, HelixConnectError\n'''
                '''        """\n'''
                '''        self._request('%(action)s', self._filter(vars()))\n'''
                '''\n''' % {
                    'action_descr': action_descr,
                    'action': c.cleaned_name,
                    'description': c.description,
                    'top_args': format_top_args(c.scheme),
                }
            )
        else:
            bits.append(
                '''    def %(action)s(\n'''
                '''%(top_args)s\n'''
                '''    ):\n'''
                '''        """\n'''
                '''        %(action_descr)s'''
                '''%(response)s'''
                '''        @raise HelixApiError, HelixConnectError\n'''
                '''        """\n'''
                '''        return self._request('%(action)s', self._filter(vars()))\n'''
                '''\n''' % {
                    'response': response_descr,
                    'action_descr': action_descr,
                    'action': c.cleaned_name,
                    'description': c.description,
                    'top_args': format_top_args(c.scheme),
                }
            )
    return ''.join(bits)

def main():
    from helixtariff.validator.validator import protocol
    helixname = 'Helixtariff'
    fname = 'generated-docs.html'
    s = generate_htmldoc_by_protocol(protocol, title='%s protocol' % helixname)
    open(fname, 'w').write(s)
    webbrowser.open(fname)

    # experimantal. Works with simple protocol only
    fname = 'generated-helixclient.py'
    s = generate_accessors_by_protocol(protocol)
    open(fname, 'w').write('class %sApi(HelixApi):\n' % helixname + s)

if __name__ == '__main__':
    main()
