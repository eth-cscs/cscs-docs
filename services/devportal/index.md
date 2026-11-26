# Developer Portal

The [Developer Portal](<https://developer.cscs.ch>) facilitates CSCS users to manage client applications’ subscriptions to an API at CSCS, such as [FirecREST](<https://docs.cscs.ch/access/firecrest/index.md#firecrest>), [CI/CD](<https://docs.cscs.ch/services/cicd/index.md#continuous-integration-continuous-deployment-cicd> "Continuous Integration / Continuous Deployment (CI/CD)") or [Alps Accounting API](<https://docs.cscs.ch/services/alps-accounting-api/index.md#alps-accounting-api>).

## Terminology

### API

An **API** is an interface exposed by CSCS to their users to allow them accessing protected resources (computing, storage, accounting data, etc.) in an automated fashion.

Examples of automated access to HPC resources are:

- A cronjob that triggers a CI/CD pipeline to test software periodically
- A workflow manager that executes workflows asynchronously
- A web application that performs unattended data transfer after a job finishes

### Application

An **application** (or “*client application*” or “*client*”) is a software created by users that consumes the resources exposed by an API.

At CSCS, it requires [OIDC/OAuth2 access tokens](<https://datatracker.ietf.org/doc/html/rfc6749#section-1.4>) to authenticate against an [Identity Provider](<#identity-provider-idp>) (IdP) in order to access the protected resources.

An application *consumes* API resources by *subscribing* to the API. At CSCS, applications can be subscribed to multiple APIs.

### Identity provider (IdP)

An **identity provider** is an entity that authenticates an application and allows accessing protected resources. In this case, CSCS provides an IdP for all its APIs.

### Production keys

Applications must identify against the CSCS IdP. To do this, users must create the **production keys** (*Consumer Key* and *Consumer Secret*) that are going to be used to authenticate.

The Developer Portal and OAuth2 use different names for the two keys:

| Developer Portal | OAuth2 name | Placeholder in the examples |
| --- | --- | --- |
| *Consumer Key* | client ID (`client_id`) | `<CONSUMER_KEY>` |
| *Consumer Secret* | client secret (`client_secret`) | `<CONSUMER_SECRET>` |

> [!WARNING]
>
> The pair Consumer Key and Secret represents a personal credential to access CSCS resources, therefore can’t be shared and must be stored securely (i.e.: not exposed in public repositories, forums, documentation, etc)

## Getting started

Start by browsing to [developer.cscs.ch](<https://developer.cscs.ch>), then sign in by clicking the `SIGN-IN` button on the top right hand corner of the page.

Once logged in, you will see a list of APIs that are available to your user.

> [!WARNING]
>
> You might not see version 1 or version 2 of some APIs. You will be able to see all the versions when you *subscribe* your Application to the API.

### Creating an application

Click on the `Applications` option at the top of the screen to manage your applications.

![FirecREST Main Page](<https://docs.cscs.ch/images/services/devportal-apis.png>)

To create a new application, click on the `ADD NEW APPLICATION` button at the top of the Applications view

![Create New App](<https://docs.cscs.ch/images/services/devportal-create-new-app.png>)

Complete the mandatory fields (marked with `*`) and make sure to give the application a unique name and select the number of requests per minute.

When finished, click on the `SAVE` button.

> [!NOTE]
>
> On your first login you will find the `DefaultApplication` which is created by default

> [!NOTE]
>
> The quota of requests per minute will be shared by all subscribers to the Application over all APIs

### Configuring production keys

Once the Application is created, create the Production Keys by clicking on `Production Keys` in the left panel:

![FirecREST production keys](<https://docs.cscs.ch/images/services/devportal-keys.png>)

Click on the `Generate Keys` button at the bottom of the page to generate the production keys of your application:

![FirecREST existing keys](<https://docs.cscs.ch/images/services/devportal-generate-keys.png>)

Once the keys are generated, you will see the pair `Consumer Key` (also known as “client id”) and `Consumer Secret` (also known as “client secret”).

![FirecREST keys](<https://docs.cscs.ch/images/services/devportal-keys-overview.png>)

> [!NOTE]
>
> At the moment, only FirecREST keys are available. The keys belong to the `firecrest-clients` realm of the CSCS IdP, so access tokens have to be [requested from that realm](<https://docs.cscs.ch/services/devportal/index.md#request-an-access-token> "Request an access token"), using the `Token Endpoint` shown under `Key Configurations`.

### Subscribe to an API

Once you have set up your Application, is time to subscribe it to an API.

To do so:

- (8.a) click on the `Subscriptions` option on the left panel
- (8.b) click the `SUBSCRIBE APIS` button
- (8.c) choose the [business plan](<https://docs.cscs.ch/services/devportal/index.md#view-information-of-apis> "View information of APIs") and the version of the API you want to subscribe to by clicking the `SUBSCRIBE` button on the right-side of the requested API.

![Devportal subscriptions](<https://docs.cscs.ch/images/services/devportal-api-subscriptions.png>)

### Request an access token

Exchange the production keys for a short-lived access token, passing the *Consumer Key* as the user name and the *Consumer Secret* as the password with the `-u` option of `curl`:

request an access token

```console
$ curl -s -X POST "https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token" \
    -u "<CONSUMER_KEY>:<CONSUMER_SECRET>" \
    --data "grant_type=client_credentials" | jq
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6...",
  "expires_in": 300,
  "refresh_expires_in": 0,
  "token_type": "Bearer",
  "not-before-policy": 0,
  "scope": "firecrest firecrest-v2 profile email"
}
```

The token is valid for 5 minutes (`expires_in` is in seconds), after which a new token has to be requested.

store the token in the ACCESS\_TOKEN environment variable

```bash
export ACCESS_TOKEN=$(curl -s -X POST "https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token" \
    -u "<CONSUMER_KEY>:<CONSUMER_SECRET>" \
    --data "grant_type=client_credentials" | jq -r .access_token)
```

Pass the token in the `Authorization: Bearer $ACCESS_TOKEN` header of every request to the API.

> [!WARNING]
>
> **`Base64(consumer-key:consumer-secret)` is a placeholder**
>
> The `CURL TO GENERATE ACCESS TOKEN` button on the `Production Keys` page shows a command that passes the keys in an `Authorization: Basic` header instead of with `-u`. The value in that header has to be the base64 encoding of `<CONSUMER_KEY>:<CONSUMER_SECRET>`, which is what `-u` generates. The text `Base64(consumer-key:consumer-secret)` stands for that value: the request fails with `Invalid client or Invalid client credentials` if it is used as written.

## Manage your applications

Back on the Subscription Management page, you can review your active subscriptions and APIs that your Application has access to.

![Devportal subscription management](<https://docs.cscs.ch/images/services/devportal-api-subscriptions-management.png>)

### Regenerate production keys

It’s a good practice to rotate or regenerate the production keys of your application to increase security.

To do this, go to the `Production Keys` view of the desired application and click on the button `REMOVE KEYS`:

![Devportal reset keys](<https://docs.cscs.ch/images/services/devportal-regenerate-keys.png>)

To regenerate the keys, refer back to the [Configuring production keys](<https://docs.cscs.ch/services/devportal/index.md#configuring-production-keys>) section.

> [!NOTE]
>
> **Info**
>
> After resetting the credentials, you will need to reconfigure your software(s) to use the new keys

### Remove your application

To delete your application (which means removing all subscriptions and production keys), refer to the Application view and click on the `DELETE` button in the top-right corner.

## View information of APIs

The Developer Portal includes information of the APIs exposed by CSCS on the API view.

Click on `APIs` button on the top of the Developer Portal, and select on the left menu the option `Overview`

![Devportal apis overview](<https://docs.cscs.ch/images/services/devportal-api-overview.png>)

The information exposed in the overview view is:

- Amount of subscriptions to the API (among all clients)
- Documentation of the API (OpenAPI reference, SDK tools, etc)
- Community information (Public repository, slack channel)
- Contact information (developers and business)
- Business plans (amount of requests per minute that are allowed in the API subscription)
- Applications owned by the user that are subscribed to the API

### API documents

Clicking in the left option `Documents` the user will be able to see the API reference with examples:

![Devportal apis reference](<https://docs.cscs.ch/images/services/devportal-api-docs.png>)

## Further information

- [WSO2 Developer Portal](<https://apim.docs.wso2.com/en/4.4.0/consume/consume-api-overview/>)
- [Open ID Connect protocol (OIDC)](<https://openid.net/developers/how-connect-works/>)
- [JSON Web Tokens](<https://www.jwt.io/introduction#what-is-json-web-token>)
- [OpenAPI initiative](<https://www.openapis.org/what-is-openapi>)
