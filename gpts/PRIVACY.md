# Growth Data Reader Privacy Policy

Last updated: September 1, 2026

Growth Data Reader is an internal, read-only analytics integration for authorized team members. It connects a custom GPT to a server-side account profile for Google Analytics 4, Google Search Console, and Google Ads.

## Data processed

The service processes query parameters supplied by the GPT and analytics or advertising report data returned by the configured Google APIs. This can include aggregated traffic, search performance, campaign, conversion, and revenue metrics.

## Credentials

Google OAuth credentials, the Google Ads developer token, and the Reader Token are stored in Google Cloud Secret Manager. They are not included in GPT instructions, knowledge files, URLs, or API responses.

## Use and retention

The Gateway uses submitted query parameters only to complete read-only API requests. The application does not intentionally persist query responses. Google Cloud platform logs may retain operational metadata according to the project administrator's logging settings.

## Sharing

Report data is returned only to callers presenting the configured Reader Token. Data is not sold or used for advertising by this integration.

## Access and deletion

Access can be revoked by rotating the Reader Token, removing the GPT Action, disabling the Cloud Run service, or removing the relevant Google account permissions.

## Contact

For access, correction, or deletion requests, contact the administrator of the INIA Google Cloud and ChatGPT workspace.
