https://api.portal.dnb.nl/

Welcome to DNB API Services. DNB API Services offer a variety of REST APIs in one unified platform to give you programmatic access to public DNB data.

Use these REST APIs with REST calls or client libraries in popular programming languages and automate your workflows.

Please note: DNB API Services is currently in preview. We value your feedback and suggestions. Please send an email to My DNB with your feedback.

Starters Guide
Welcome to DNB API Services! DNB provides a range of APIs that enable you to integrate our services into your applications. This page offers information on how to access DNB APIs for public use.

Registration
In order to utilize our APIs, you must have an My DNB account. Please go to About My DNB account and follow the steps to create an account if you do not already have one.

Account details
If you already have a My DNB account and want to change you contact details, change password or delete your account, please navigate to My DNB - My details.

APIs
Once logged in, the APIs page will present you with a list of available APIs. Each API is accompanied by a brief description. You can utilize the search bar to find the API that is relevant to your requirements. Detailed OpenAPI documentation for each API, including parameters and sample requests, is provided. To start using APIs, you need to obtain access through a subscription to a product.

Product subscriptions
A product is a collection of one or multiple APIs. To discover the available products, please visit the Products page. When you subscribe to a product, you will receive a pair of subscription keys that allow you to access the APIs within that product. To ensure your API requests are acknowledged and permitted, and to view analytics under the Reports page, you need to create a subscription with your own chosen name.

When making a call to a DNB API, it is mandatory to include a subscription key in the request. Provide the key as the value for the Ocp-Apim-Subscription-Key HTTP header in your requests. When testing an API through the DNB API Services environment, the key you created for a product will be automatically added to the request. Alternatively, you can choose a different key from the dropdown list. Please note that subscriptions are subject to a rate limit of 30 calls per minute.

Follow the steps below to create a product subscription:

Go to the Products page.

Click on the desired product. All publicly available APIs are categorized under the product Public.

Under Your subscriptions, define your own subscription name and click Subscribe.

Accept any applicable terms of use and click confirm.

An automatically generated email will confirm your registration request for the chosen product.

Upon completing the above steps, you will be redirected to your personal profile page within the DNB API Services environment. This page will display all your subscriptions. We recommend regenerating your keys at least every six months by clicking Regenerate on the personal profile page.

Contact and support
We are delighted to assist you with any inquiries you may have regarding DNB API Services. If you have a question about a specific API, please refer to the contact information provided in the API description, if available. For general API questions, please go to My DNB Contact.