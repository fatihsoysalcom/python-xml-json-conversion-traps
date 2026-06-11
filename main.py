import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def xml_to_dict(element):
    """
    Recursively converts an XML ElementTree element into a dictionary.
    This function aims to preserve XML structure, attributes, and text content
    in a JSON-friendly format, addressing common conversion 'traps'.
    """
    # If the element has no children, no attributes, and only text content,
    # return the text directly for a cleaner JSON representation.
    # This avoids {"tag": {"#text": "value"}} for simple cases.
    if not list(element) and not element.attrib and element.text and element.text.strip():
        return element.text.strip()

    # Initialize dictionary for the current element
    result = {}

    # Trap 1: Preserving Attributes
    # XML attributes are converted to dictionary entries prefixed with '@'.
    # This prevents data loss where attributes carry important information.
    for attr, value in element.attrib.items():
        result[f"@{attr}"] = value

    # Trap 2: Handling Text Content vs. Child Elements
    # If an element has text content, it's stored under the '#text' key.
    # This distinguishes it from child elements and preserves it when an element
    # also has attributes or children.
    if element.text and element.text.strip():
        result["#text"] = element.text.strip()

    # Process child elements
    # Use defaultdict to easily group multiple children with the same tag.
    children = defaultdict(list)
    for child in element:
        children[child.tag].append(xml_to_dict(child))

    for tag, items in children.items():
        # Trap 3: Handling Lists of Sibling Elements
        # If multiple children share the same tag, they are converted into a JSON array.
        # This prevents data loss or overwriting when XML has repeating elements.
        if len(items) == 1:
            result[tag] = items[0]
        else:
            result[tag] = items # Already a list

    # If the element has no attributes, no text, and no children, it's an empty element.
    # An empty dictionary {} is a reasonable representation.
    # Example: <empty_element/> -> "empty_element": {}
    return result

# Sample XML content (as a string)
# This XML demonstrates various structures that can lead to conversion 'traps'.
xml_string = """
<catalog last_updated="2023-10-27">
  <book id="bk101" category="fiction">
    <author>Gambardella, Matthew</author>
    <title>XML Developer's Guide</title>
    <genre>Computer</genre>
    <price currency="USD">44.95</price>
    <publish_date>2000-10-01</publish_date>
    <description>An in-depth look at creating applications with XML.</description>
    <tags>
        <tag>XML</tag>
        <tag>Programming</tag>
        <tag>Guide</tag>
    </tags>
  </book>
  <book id="bk102" category="non-fiction">
    <author>Ralls, Kim</author>
    <title>Midnight Rain</title>
    <genre>Fantasy</genre>
    <price currency="USD">5.95</price>
    <publish_date>2000-12-16</publish_date>
    <description>A young woman discovers her ancestral past.</description>
  </book>
  <empty_element/>
  <element_with_cdata><![CDATA[This is <CDATA> content with special characters & entities.]]></element_with_cdata>
</catalog>
"""

# Parse the XML string into an ElementTree root element
root = ET.fromstring(xml_string)

# Convert the XML root element and its children to a dictionary.
# The outermost dictionary uses the root element's tag as its key.
converted_dict = {root.tag: xml_to_dict(root)}

# Convert the dictionary to a JSON string with pretty printing (indent=2).
# ensure_ascii=False allows non-ASCII characters to be output directly.
json_output = json.dumps(converted_dict, indent=2, ensure_ascii=False)

# Print the resulting JSON
print(json_output)

# --- Additional Notes on Traps Handled by This Conversion Logic ---
# Trap 4: CDATA Sections
# XML's CDATA sections (e.g., <element_with_cdata><![CDATA[...]]></element_with_cdata>)
# are automatically parsed by ElementTree as regular text content.
# This conversion correctly extracts and places that text into the JSON output.
# The text "This is <CDATA> content with special characters & entities." will appear directly.

# Trap 5: Empty Elements
# An empty element like <empty_element/> is converted to "empty_element": {}.
# This preserves its existence in the hierarchy, even if it carries no data.
