package ua.agrichain.work03.service.tools;

import org.springframework.stereotype.Component;

@Component
public class CalculatorTool {

    public double estimateCost(String policyRule, int requestedHours) {
        double rate = policyRule.contains("8H") ? 120.0 : 95.0;
        return rate * requestedHours;
    }
}