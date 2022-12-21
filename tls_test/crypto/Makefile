.PHONY: all clean

material: generate.sh tls-server.conf trusted-root-ca.conf untrusted-root-ca.conf
	./generate.sh
	mkdir -p material.new/servers/valid material.new/servers/invalid material.new/servers/untrusted
	mkdir -p material.new/trusted-ca material.new/untrusted-ca
	cp ca/trusted-root-ca.crt material.new/trusted-ca/ca.pem
	cp ca/untrusted-root-ca.crt material.new/untrusted-ca/ca.pem
	cp certs/tls-inferer-gasp.crt material.new/servers/valid/cert.pem
	cp certs/tls-inferer-gasp.key material.new/servers/valid/key.pem
	cp certs/invalid-tls-inferer-gasp.crt material.new/servers/invalid/cert.pem
	cp certs/invalid-tls-inferer-gasp.key material.new/servers/invalid/key.pem
	cp certs/untrusted-tls-inferer-gasp.crt material.new/servers/untrusted/cert.pem
	cp certs/untrusted-tls-inferer-gasp.key material.new/servers/untrusted/key.pem
	rm -rf material.bak
	mv material material.bak || true
	mv material.new material

certs/%.crt: trusted-root-ca.conf
	@./emit_valid_server_cert.sh $$(basename $(@:.crt=))

clean:
	rm -rf *~ ca certs crl material material.bak material.new
