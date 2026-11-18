package ua.agrichain.work03.service.tools;

import org.springframework.stereotype.Component;

@Component
public class RuleSearchTool {

    public String findPolicyRule(String equipmentType, String region) {
        if (equipmentType.equalsIgnoreCase("sprayer") && region.equalsIgnoreCase("north")) {
            return "MAX_8H_PER_DAY";
        }
        return "STANDARD_12H";
    }
}