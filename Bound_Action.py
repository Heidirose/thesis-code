import Current_Goal
import TheAgent
import Fact
from copy import copy

#This represents an action that has been put on the planning stack. An action on the stack consists
#of an action rule, and a dictionary of binding information that specifies what objects have been
#bound to the variables in the action rule.
class Bound_Action:

    def __init__(self, action_rule, bindings, goals_to_accomplish):
        self.action_rule = action_rule
        self.bindings = bindings
        self.goals = goals_to_accomplish #What goals is this action rule supposed to achieve?

    def score_for_bindings(self):
        return self.action_rule.score_for_bindings()

    def get_action_rule(self):
        return self.action_rule

    def id_of_action_rule(self):
        return self.action_rule.get_id()

    #Returns a Current Goal object containing all the preconditions (with the bindings applied)
    def goals_for_preconditions(self):
        reliable_preconditions = self.action_rule.get_reliable_preconditions() + list(self.action_rule.get_constraint_set().get_constraints())
        new_goals = []
        for fact in reliable_preconditions:
            spec = fact.get_specific_copy_with_dictionary(self.bindings)
            new_goals.append(spec)
        return Current_Goal.Current_Goal(new_goals, "Full")

    #Returns a Current Goal object for the goals that this bound ar is expected to accomplish
    #It is possible that this will need to be updated right before it is used, but for now turning a blind eye to this
    def goals_expected_to_accomplish(self):
        bound_goals = []
        for fact in self.goals:
            bound_goals.append(fact.get_specific_copy_with_dictionary(self.bindings))
        return Current_Goal.Current_Goal(bound_goals, "Expected")

    def action_type(self):
        return self.action_rule.get_intention().get_predicate()

    #Writing this in a long winded form to ease debugging
    def action_parameter_unbound(self):
        #Firsty, does this action rule even have an intention parameter?
        if self.action_rule.intention_param() is None:
            return False
        #Actually, it always must be a variable
        ##Now, is the intention param a variable?
        #if not self.action_rule.intention_param().is_var():
            #return False
        #Does the intention param have a binding?
        if self.action_rule.intention_param() not in self.bindings:
            return True
        #But if it is in the bindings, it still might not be suitable. i.e. is it bound to a var?
        if self.bindings[self.action_rule.intention_param()].is_var():
            return True
        else:
            return False

    #If the intention param is unbound, we might want to bind a random suitable object to it
    def bind_random_object_to_intention(self):
        if self.action_parameter_unbound():
            type_needed = self.action_rule.intention_param_type()
            obj_to_use = self.__find_suitable_object(type_needed)
            param_for_obj = Fact.Param(obj_to_use, False, None)
            self.bindings[self.action_rule.intention_param()] = param_for_obj

    #Note: This is does not handle the place type correctly.
    def __find_suitable_object(self, type_needed):
        if type_needed == "p":
            x = 50 #NEED TO DO THIS PROPERLY (checking if this at least stops the crashing)
            y = 50 #NEED TO DO THIS PROPERLY
            return (x, y)
            #Special case, need a place type object
        else:
            candidates = TheAgent.The_Agent().controller().objects_currently_in_world()
            for candidate in candidates:
                if not self.__obj_used_in_action(candidate) and Fact.Param.type_of_name(candidate) == type_needed:
                    return candidate
        return None

    def __obj_used_in_action(self, obj):
        return False

    def action_parameter(self):
        return self.bindings[self.action_rule.intention_param()]

    def stack_data_type(self):
        return "Action"

    def number_of_goals_expected_to_accomplish(self):
        return len(self.goals)


    def goals_to_accomplish(self):
        return self.goals

    def print_summary(self):
        print(self.action_rule.summary())
        for key in self.bindings:
            print(str(key) + " -> " + str(self.bindings[key]))
        for goal in self.goals:
            print(goal)

    def update_bindings(self, additional_bindings):
        for binding in additional_bindings:
            if binding not in self.bindings:
                self.bindings[binding] = additional_bindings[binding]
            elif additional_bindings[binding] != self.bindings[binding]:
                print("Potential error")
        self.__clean_bindings()

    def __clean_bindings(self):
        for key in copy(self.bindings): #Can't remember the method to get key set. It always changes
            if key in self.bindings: #hasn't already been deleted
                value = self.bindings[key]
                while value in self.bindings:
                    old_val = value
                    value = self.bindings[value]
                    del self.bindings[old_val]
                self.bindings[key] = value
