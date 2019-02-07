import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        in_kb = False
        indent_count = 0
        if isinstance(fact_or_rule, Fact):
            for facts in self.facts:
                if facts == fact_or_rule:
                    in_kb = True
                    s = self.get_state_string(facts)
                    if facts.asserted == True:
                        s += ' ASSERTED\n'
                    else:
                        s += '\n'
                        for supps in facts.supported_by:
                            for supp in supps:
                                s += self.explain_helper(supp, indent_count, True)
                    return s
            if in_kb == False:
                err = "Fact is not in the KB"
                return err
        elif isinstance(fact_or_rule, Rule):
            for rules in self.rules:
                if rules == fact_or_rule:
                    in_kb = True
                    s = self.get_state_string(rules)
                    if rules.asserted == True:
                        s += ' ASSERTED\n'
                    else:
                        s += '\n'
                        for supps in rules.supported_by:
                            for supp in supps:

                                s += self.explain_helper(supp,indent_count,True)
                    return s
            if in_kb == False:
                err = "Rule is not in the KB"
                return err

    def explain_helper(self, fact_or_rule, indent_count, first):
        if fact_or_rule.asserted == True and first == True:
            s = '  SUPPORTED BY\n'
        else:
            s = ''
        indent_count += 2
        if isinstance(fact_or_rule, Fact):
            for facts in self.facts:
                if facts == fact_or_rule:
                    #s = (' ' * indent_count) + '  SUPPORTED BY\n'
                    #indent_count += 1
                    s += ('  ' * indent_count) + self.get_state_string(facts)
                    if facts.asserted == True:
                        s += ' ASSERTED\n'
                    else:
                        s += '\n' + ('  ' * indent_count) + '  SUPPORTED BY\n'
                        for supps in facts.supported_by:
                            for supp in supps:
                                '''s += (' ' * indent_count) + ' ' + self.get_state_string(supp) + '\n'
                                if supp.supported_by != []:
                                    #indent_count = indent_count + 1
                                    for sp in supp.supported_by:
                                        for ps in sp:
                                            s += self.explain_helper(ps, indent_count)'''
                                s += self.explain_helper(supp,indent_count,False)
                    return s
        elif isinstance(fact_or_rule, Rule):
            for rules in self.rules:
                if rules == fact_or_rule:

                    s += ('  ' * indent_count) + self.get_state_string(rules)
                    if rules.asserted == True:
                        s += ' ASSERTED\n'
                    else:
                        s += '\n' + ('  ' * indent_count) + '  SUPPORTED BY\n'
                        for supps in rules.supported_by:
                            for supp in supps:
                                s += self.explain_helper(supp,indent_count,False)
                    return s
    def get_state_string(self, fr):
        if isinstance(fr, Fact):
            s = 'fact: (' + fr.statement.predicate + ' ' + fr.statement.terms[0].term.element + ' ' + fr.statement.terms[1].term.element + ')'
            return s
        elif isinstance(fr, Rule):
            s = 'rule: (('
            if len(fr.lhs) > 1:
                fcount = 0
                for stats in fr.lhs:
                    if fcount == 0:
                        s += stats.predicate
                        for terms in stats.terms:
                            s += ' ' + terms.term.element
                        s += ')'
                        fcount = fcount + 1
                    else:
                        s += ', (' + stats.predicate
                        for terms in stats.terms:
                            s += ' ' + terms.term.element
                        s += ')'
            else:
                s += fr.lhs[0].predicate
                for terms in fr.lhs[0].terms:
                    s += ' ' + terms.term.element
                s += ')'
            #s += ') -> (' + fr.rhs.predicate + ' ' + fr.rhs.terms[0].term.element + ' ' + fr.rhs.terms[1].term.element + ')'
            s += ') -> (' + fr.rhs.predicate
            for stats in fr.rhs.terms:
                s += ' ' + stats.term.element
            s += ')'
            return s

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment
