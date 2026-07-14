"""External calls: third-party APIs, boto3/AWS SDK, object storage, email/SMS
providers, etc. May read/write models directly when persisting something tied
to the call itself (e.g. logging it) — otherwise keep this layer stateless and
return data to the calling controller. Empty in a fresh scaffold — add one
module per integration as you wire them in."""
