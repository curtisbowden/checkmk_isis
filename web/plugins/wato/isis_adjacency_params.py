from ipaddress import ip_network
from typing import List
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    RulespecGroupCheckParametersDiscovery,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    Checkbox,
    ListOfStrings,
    Labels,
    MKUserError,
)
from cmk.gui.i18n import _


def _validate_spec_subnet(value: List, varprefix) -> bool:
    for subnet in value:
        try:
            ip_network(subnet)
        except ValueError as e:
            raise MKUserError(
                varprefix,
                _(f"{e}"),
            )
    return True

def _parameter_valuespec_isis_adjacency_discovery() -> Dictionary:
    return Dictionary(
        required_keys=["subnets"],
        elements=[
            (
                "subnets",
                Dictionary(
                    required_keys=["subnets", "negate"],
                    elements=[
                        (
                            "subnets",
                            ListOfStrings(
                                title=_("Subnets"),
                                allow_empty=False,
                                validate=_validate_spec_subnet,
                                help=_('If an IS-IS neighbor is within specified subnets, it will get discovered.'),
                            )
                        ),
                        (
                            "negate",
                            Checkbox(
                                title=_("Negate"),
                                help=_("Negate the subnet match. If checked, the rule will match if the IS-IS neighbor is not within the specified subnets."),
                                true_label=_("negated"),
                                default_value=False,
                            ),
                        ),
                    ]
                )
            ),
            (
                "labels",
                Labels(
                    title=_("Discovery label"),
                    world=Labels.World.CONFIG,
                    label_source=Labels.Source.RULESET,
                    help=_("Labels to be assigned to the discovered services."),
                ),
            ),
        ]
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="dict",
        name="isis_adjacency_discovery",
        valuespec=_parameter_valuespec_isis_adjacency_discovery,
        title=lambda: _("IS-IS Neighbor discovery"),
    )
)
