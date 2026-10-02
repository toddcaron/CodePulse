<cfhttp url="https://example.invalid" method="get"></cfhttp>
<cfmail to="recipient@example.invalid" from="sender@example.invalid" subject="Sample">Sample</cfmail>
<cfschedule action="update" task="sample" operation="HTTPRequest" url="https://example.invalid" interval="daily">
<cfreport template="sample.cfr"></cfreport>