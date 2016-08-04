# Api.ai MedBot Webhook

This is a really simple webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response with based FDA and RxNorm drug data.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

The service packs the drug inquiry/interactions result in the Api.ai webhook-compatible response JSON and returns it to Api.ai.

