# mix
Mix of scripts
- *jinja2_vlan_list.py*
	Used to build a base-config file for any switch (Brocade or Cisco so far)
- *base-config-brocade.j2*
	Jinja2 Template for Brocade switches, used in jinja2_vlan_list.py	
- *base-config.j2*
	Jinja2 Template for Cisco switches, used in jinja2_vlan_list.py
- *password-change*
	Changes password on all the devices, regardless of vendor
- *snmp-check*
	Calculates Inbound/Outbound rate on selected interface
- *test-ping*
	Tests ping reachability to end-hosts, connected to particular switch
- *test-rancid*
	Tests, whether any end-host, connected to a switch ports got changed, before and after the new config is placed.
