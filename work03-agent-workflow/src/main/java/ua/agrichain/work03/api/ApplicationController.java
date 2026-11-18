package ua.agrichain.work03.api;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import ua.agrichain.work03.api.dto.ApplicationResponse;
import ua.agrichain.work03.api.dto.SubmitApplicationRequest;
import ua.agrichain.work03.service.WorkflowService;

@RestController
@RequestMapping("/api/v1/applications")
public class ApplicationController {

    private final WorkflowService workflowService;

    public ApplicationController(WorkflowService workflowService) {
        this.workflowService = workflowService;
    }

    @PostMapping
    public ResponseEntity<ApplicationResponse> submit(@Valid @RequestBody SubmitApplicationRequest request) {
        return ResponseEntity.ok(workflowService.handle(request));
    }
}