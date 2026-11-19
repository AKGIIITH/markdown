# Let me set a CSS class on tables generated from Markdown

I publish reports that contain several Markdown tables. My stylesheet uses
the class `report-table`, and currently I have to edit the generated HTML
to apply that style to each table.

I'd like to configure the tables extension once with `table_class="report-table"`
and have every generated `<table>` in that document carry that class. Some
reports also use a compact layout, so a value such as `"report-table compact"`
should apply both CSS classes.

When I leave the option unset, ordinary Markdown tables should render as they
do today, without a class attribute. Their headers and cell contents should
be preserved in either case.

Baseline: 2c96e36ba4750cf18583d62e2fcecff49e077419
