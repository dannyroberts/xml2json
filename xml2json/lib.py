from __future__ import absolute_import
import lxml.etree
import six

xml2json_parser = lxml.etree.XMLParser(remove_comments=True)


def xml2json(xml_string):
    """
    raises xml2json.XMLSyntaxError

    """
    try:
        xml = lxml.etree.fromstring(xml_string, parser=xml2json_parser)
    except lxml.etree.XMLSyntaxError:
        # conveniently lxml.etree.XMLSyntaxError equals xml2json.XMLSyntaxError
        raise

    return convert_xml_to_json(xml)


def convert_xml_to_json(xml, last_xmlns=None):
    try:
        tag = six.text_type(xml.tag.split('}')[1])
    except IndexError:
        # This case comes up when you have something like
        #     <n0:foo xmlns:n0="http://foo.com/bar">
        #         <bar>baz</bar>
        #     </n0:foo>
        # in which case tag for bar is not '{}bar' but simply 'bar'
        tag = six.text_type(xml.tag)
        xmlns = None
    else:
        xmlns = six.text_type(xml.tag.split('}')[0][1:])


    attributes = {}
    for key, value in xml.attrib.items():
        attributes[u'@{0}'.format(key)] = six.text_type(value)

    children = {}
    for child in xml:
        key, value = convert_xml_to_json(child, last_xmlns=xmlns)
        key = six.text_type(key)
        if key in children:
            prev_value = children[key]
            if isinstance(prev_value, list):
                prev_value.append(value)
            else:
                children[key] = [prev_value, value]
        else:
            children[key] = value

    text = xml.text or ''
    text = six.text_type(text)

    # check for None because you don't want something like
    # {'@xmlns': None, '#text': 'foo'}
    if xmlns not in (last_xmlns, None):
        attributes[u'@xmlns'] = xmlns

    if attributes or children:
        result = attributes
        result.update(children)
        if text.strip():
            result[u'#text'] = text
    else:
        result = text

    return tag, result
