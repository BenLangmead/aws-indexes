<div class="home-hero">
  <p class="home-lead">
    Thanks to the <a href="https://aws.amazon.com/opendata/public-datasets/">AWS Open Data Sponsorship Program</a>, indexes are freely available via <strong>HTTPS</strong> and <strong>S3</strong>.
  </p>
</div>

{% assign usage = site.data.usage_highlights %}
{% if usage.cards %}
<section class="usage-highlights" aria-labelledby="usage-highlights-heading">
  <div class="usage-highlights-header">
    <h2 id="usage-highlights-heading">Usage snapshot</h2>
    <p>Measured from AWS Cost Explorer and CloudWatch. Current-month figures cover {{ usage.period.label }}.</p>
  </div>
  <div class="usage-highlight-grid">
    {% for card in usage.cards %}
    <div class="usage-highlight">
      <span class="usage-highlight-value">{{ card.value }}</span>
      <span class="usage-highlight-label">{{ card.label }}</span>
      <span class="usage-highlight-detail">{{ card.detail }}</span>
    </div>
    {% endfor %}
  </div>
  <p class="usage-highlight-note">Server access logs are available back to {{ usage.first_known_log_date }} for more detailed file-level analysis.</p>
</section>
{% endif %}

<h2 class="tool-grid-heading">Browse by tool</h2>
<div class="tool-grid">
{% for nav in site.navigation %}
  {% unless nav.url contains "://" or nav.url == '/' %}
  {% assign card_desc = nav.blurb %}
  <a class="tool-card" href="{{ nav.url | relative_url }}">
    {{ nav.title }}
    {% if card_desc %}<span class="tool-card-desc">{{ card_desc }}</span>{% endif %}
  </a>
  {% endunless %}
{% endfor %}
</div>

<div class="home-after-grid" markdown="1">

From *within AWS*, e.g. from an EC2 instance, you can use the [AWS CLI](https://aws.amazon.com/cli/) and its `s3 co` or `s3 sync` commands like this:

```buildoutcfg
aws s3 cp s3://genome-idx/bt/grch38_1kgmaj.zip .
```

You can also initiate transfers using the [AWS console](https://aws.amazon.com/console/), the Python [`boto3` library](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), and various other tools and libraries.

Access to files in the [AWS Open Data Sponsorship Program](https://aws.amazon.com/opendata/open-data-sponsorship-program/) is *free*.  This is true whether you use the HTTPS or the S3 URL.  For S3 URLs, the transfer is free even if it crosses an AWS region boundary; there is no [inter-regional data transfer fee](https://aws.amazon.com/s3/pricing/).

</div>
