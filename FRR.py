from base_node import Router

class FRR(Router):

    PRIVATEDIRS = ["/etc/frr", "/var/run/frr"]

    DAEMONS = """
zebra=yes
ospf6d=yes

vtysh_enable=yes
zebra_options=" -s 90000000 --daemon -A 127.0.0.1"
ospf6d_options=" --daemon -A ::1"
"""

    VTYSH = """\
hostname {name}
service integrated-vtysh-config
"""

    def __init__(self, name, inNamespace=True, **params):
        params.setdefault("privateDirs", [])
        params["privateDirs"].extend(self.PRIVATEDIRS)
        super().__init__(name, inNamespace=inNamespace, **params)

    def config(self, **params):
        super().config(**params)
        self.start_frr_service()

    def set_conf(self, file, conf):
        """set frr config"""
        self.cmd("""\
cat << 'EOF' | tee {}
{}
EOF""".format(file, conf))

    def start_frr_service(self):
        """start FRR"""
        self.set_conf("/etc/frr/daemons", self.DAEMONS)
        self.set_conf("/etc/frr/vtysh.conf", self.VTYSH.format(name=self.name))
        print(self.cmd("/usr/lib/frr/frrinit.sh start"))

    def vtysh_cmd(self, cmd: str):
        """exec vtysh commands"""
        cmds = cmd.split("\n")
        vtysh_cmd = "vtysh"
        for c in cmds:
            vtysh_cmd += " -c \"{}\"".format(c)
        return self.cmd(vtysh_cmd)
