# SoftLayer Java Data Type Generator

## What this does

Generates a Java class based on the webpage of a SoftLayer Data Type reference API. (E.G. https://sldn.softlayer.com/reference/datatypes/SoftLayer_Account)

## Usage
1. `git clone` this repository.
2. `pip install -r requirements.txt` (May want to create a virtualenv first)
3. `python generate.py -p <package name> <URL to SoftLayer Data Type API reference>`
4. See `python generate.py --help` for full usage options.

## Example
`python generate.py -p my.company.com https://sldn.softlayer.com/reference/datatypes/SoftLayer_Account`

The command above will generate a file named `Account.java` in the current folder with the following contents:

```java
package my.company.com;

import java.util.Date;

public class Account {
  private Integer accountStatusId;
  private String address1;
  private String address2;
  private Integer allowedPptpVpnQuantity;
  private String alternatePhone;
  private Integer brandId;
  private String city;
  private Boolean claimedTaxExemptTxFlag;
  private String companyName;
  private String country;
  private Date createDate;
  private String email;
  private String faxPhone;
  private String firstName;
  private Integer id;
  private Integer isReseller;
  private String lastName;
  private Boolean lateFeeProtectionFlag;
  private Date modifyDate;
  private String officePhone;
  private String postalCode;
  private String state;
  private Date statusDate;

}
```

## Notes
* Relational and Count properties are not included.
* Getters/setters aren't implemented. Your IDE can do this task for you and you can choose how to do it.
* Wrapper types are used instead of primitives; this makes it easier to discern when a property was missing from an unmarshalling operation, rather than being present but set to its default value.
* Classes should be ready to be used by [Jackson](https://github.com/FasterXML/jackson) without any field annotations (once the getters/setters are defined) as the field names match 1-1 with the property names.

## Background

The [SoftLayer APIs](https://sldn.softlayer.com/reference/overview) are pretty well documented.  Unfortunately, there doesn't appear to be an XSD for their [REST API](http://sldn.softlayer.com/article/rest), meaning you can't auto-generate Java classes using [`xjc`](http://docs.oracle.com/javase/6/docs/technotes/tools/share/xjc.html). However, this is a problem for me as I'm lazy and don't like copying and pasting a bunch of field names to make a Java class.

### Python to rescue

Thankfully, the [SoftLayer Data Types](https://sldn.softlayer.com/reference/datatypes/) are fairly well-documented and using [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) made it easy to extract the property names and their types in order to convert the result into a Java class.
