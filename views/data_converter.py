from bottle import Bottle, request, response, template
import json
import yaml
import xml.etree.ElementTree as ET
import csv

app = Bottle()

@app.route('/')
def index():
    return template('templates/data_converter.html')

@app.route('/', method='POST')
def data_converter():
    try:
        data = request.body.read().decode('utf-8')
        operation = request.headers.get('Operation')

        if operation == 'json-to-yaml':
            yaml_data = yaml.dump(json.loads(data))
            response.content_type = 'text/plain'
            return yaml_data

        elif operation == 'yaml-to-json':
            json_data = json.dumps(yaml.load(data, Loader=yaml.Loader))
            response.content_type = 'text/plain'
            return json_data

        elif operation == 'json-to-xml':
            json_data = json.loads(data)
            root = ET.Element('root')
            convert_to_xml(json_data, root)
            xml_data = ET.tostring(root, encoding='unicode')
            return xml_data


        elif operation == 'xml-to-json':
            root = ET.fromstring(data)
            json_data = convert_xml_to_json(root)
            response.content_type = 'text/plain'
            return json.dumps(json_data)

        elif operation == 'json-to-csv':
            json_data = json.loads(data)
            csv_data = convert_json_to_csv(json_data)
            response.content_type = 'text/plain'
            return csv_data

        else:
            response.status = 400
            return 'Invalid operation.'

    except Exception as e:
        response.status = 400
        return str(e)





def convert_to_xml(data, parent_element):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    sub_element = ET.SubElement(parent_element, key)
                    convert_to_xml(item, sub_element)
            elif isinstance(value, dict):
                sub_element = ET.SubElement(parent_element, key)
                convert_to_xml(value, sub_element)
            else:
                sub_element = ET.SubElement(parent_element, key)
                sub_element.text = str(value)
    elif isinstance(data, list):
        for item in data:
            convert_to_xml(item, parent_element)
    else:
        parent_element.text = str(data)







def convert_xml_to_json(element):
    data = {}
    for child in element:
        if child:
            if child.tag in data:
                if not isinstance(data[child.tag], list):
                    data[child.tag] = [data[child.tag]]
                data[child.tag].append(convert_xml_to_json(child))
            else:
                data[child.tag] = convert_xml_to_json(child)
        else:
            data[child.tag] = child.text
    return data

def convert_json_to_csv(json_data):
    csv_data = ''
    if isinstance(json_data, dict):
        csv_data += ','.join(json_data.keys()) + '\n'
        csv_data += ','.join(str(value) for value in json_data.values()) + '\n'
    elif isinstance(json_data, list):
        if isinstance(json_data[0], dict):
            headers = ','.join(json_data[0].keys())
            csv_data += headers + '\n'
            for item in json_data:
                csv_data += ','.join(str(value) for value in item.values()) + '\n'
    return csv_data
