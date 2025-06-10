# Object Storage

!!! note
    This page is currently incomplete and it is being updated following recent developments.

## S3

CSCS offers a public cloud object storage service, based on the Ceph Object Gateway. The service can be accessed from S3-compatible clients.

### General Information

* __Endpoint__: [https://rgw.cscs.ch](https://rgw.cscs.ch)
* __URL__: path-style in the format `https://rgw.cscs.ch/%(bucket)s/key-name`
* __Publicly accessible object links__: `https://rgw.cscs.ch/<tenant>:<bucket-name>/key-name`
    *  after setting proper bucket policy

## Usage Examples

### AWS CLI

#### Configuration

The first step is to configure the profile:

```console
$ aws configure --profile naret-testuser
AWS Access Key ID [None]: [REDACTED]
AWS Secret Access Key [None]: [REDACTED]
Default region name [None]: cscs-zonegroup
Default output format [None]:
```

Then, settings such as the default endpoint and the path-style URLs can be placed in the configuration file:

```toml
[profile naret-testuser]
endpoint_url = https://rgw.cscs.ch
region = cscs-zonegroup
s3 =
    addressing_style = path
```

#### Creating a pre-signed URL

```console
$ aws --profile=naret-testuser s3 presign s3://test-bucket/file.txt --expires-in 300
 
https://rgw.cscs.ch/test-bucket/file.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=IA6AOCNMKPDXQ0YNA3DP%2F20241209%2Fcscs-zonegroup%2Fs3%2Faws4_request&X-Amz-Date=20241209T080748Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=f2e2adb457f6fd43401124e4ea2650fba528e614ab661f9c05e2fa2e77691b5d
```

Notice that the tenant part is missing from the URL: this is because S3 doesn't natively deal with multitenancy.
The correct object is retrieved based on the access key.
A more thorough explanation can be found in the [RGW documentation](https://docs.ceph.com/en/reef/radosgw/multitenancy/#s3).

#### Making a bucket's contents anonymously accessible from the Internet

First, a bucket policy needs to be written:

```json title="test-public-bucket-anon-from-internet.json"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": [
        "arn:aws:s3:::test-public-bucket/*",
        "arn:aws:s3:::test-public-bucket"
      ]
    }
  ]
}
```

Then, it can be applied to the bucket:

```console
$ aws --profile=naret-testuser s3api put-bucket-policy \
      --bucket test-public-bucket --policy \
      file://test-public-bucket-anon-from-internet.json
```

At this point, the objects in test-public-bucket are accessible via direct links:

```console
$ s3cmd --configure
 
Enter new values or accept defaults in brackets with Enter.
Refer to user manual for detailed description of all options.
 
Access key and Secret key are your identifiers for Amazon S3. Leave them empty for using the env variables.
Access Key: [REDACTED]
Secret Key: [REDACTED]
Default Region [US]: cscs-zonegroup
 
Use "s3.amazonaws.com" for S3 Endpoint and not modify it to the target Amazon S3.
S3 Endpoint [s3.amazonaws.com]: rgw.cscs.ch
 
Use "%(bucket)s.s3.amazonaws.com" to the target Amazon S3. "%(bucket)s" and "%(location)s" vars can be used
if the target S3 system supports dns based buckets.
DNS-style bucket+hostname:port template for accessing a bucket [%(bucket)s.s3.amazonaws.com]: rgw.cscs.ch/%(bucket)s
 
Encryption password is used to protect your files from reading
by unauthorized persons while in transfer to S3
Encryption password:
Path to GPG program:
 
When using secure HTTPS protocol all communication with Amazon S3
servers is protected from 3rd party eavesdropping. This method is
slower than plain HTTP, and can only be proxied with Python 2.7 or newer
Use HTTPS protocol [Yes]: Yes
 
On some networks all internet access must go through a HTTP proxy.
Try setting it here if you can't connect to S3 directly
HTTP Proxy server name:
 
New settings:
  Access Key: [REDACTED]
  Secret Key: [REDACTED]
  Default Region: cscs-zonegroup
  S3 Endpoint: rgw.cscs.ch
  DNS-style bucket+hostname:port template for accessing a bucket: rgw.cscs.ch/%(bucket)s
  Encryption password:
  Path to GPG program: None
  Use HTTPS protocol: True
  HTTP Proxy server name:
  HTTP Proxy server port: 0
```

And then confirm.

__IMPORTANT__: The configuration is not complete yet.

```console
$ s3cmd ls s3://test-bucket
ERROR: S3 error: 403 (SignatureDoesNotMatch)
```

To fix this, it is necessary to edit the `.s3cfg` file, normally located in the user's home directory, and change the `signature_v2` setting to true.

```console
$ cat .s3cfg | grep signature_v2
signature_v2 = True
 
$ s3cmd ls s3://test-bucket
2024-12-09 08:05           15  s3://test-bucket/file.txt
```

### Cyberduck

#### Configuration

In order to be able to connect to the S3 endpoint using Cyberduck, a profile supporting path-style requests must be downloaded from [here](https://profiles.cyberduck.io/S3%20(Deprecated%20path%20style%20requests).cyberduckprofile) or copied from below.

```xml title="S3 (Deprecated path style requests).cyberduckprofile"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Protocol</key>
        <string>s3</string>
        <key>Vendor</key>
        <string>s3-path-style</string>
        <key>Scheme</key>
        <string>https</string>
        <key>Description</key>
        <string>S3 (Deprecated path style requests)</string>
        <key>Hostname Configurable</key>
        <true/>
        <key>Port Configurable</key>
        <true/>
        <key>Username Configurable</key>
        <true/>
        <key>Properties</key>
        <array>
            <string>s3.bucket.virtualhost.disable=true</string>
        </array>
    </dict>
</plist>
```

![cyberduck](../images/storage/cyberduck.png)
