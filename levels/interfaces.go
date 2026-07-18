package levels

import "time"

const (
    ConfidenceThresholdCritical = 0.731
)

type TruthLevel int

const (
    L1_Factual TruthLevel = iota
    L2_Logical
    L3_Epistemic
)

type ValidationResult struct {
    Level               TruthLevel  `json:"level"`
    Valid               bool        `json:"valid"`
    Confidence          float64     `json:"confidence"`
    ConfidenceThreshold float64     `json:"confidence_threshold"`
    RequiresContinuum  bool        `json:"requires_continuum"`
    Reason              string      `json:"reason"`
    Timestamp           time.Time   `json:"timestamp"`
    Metadata            map[string]interface{} `json:"metadata"`
    Checks              []string    `json:"checks,omitempty"`
    Errors              []string    `json:"errors,omitempty"`
}

type Validator interface {
    Validate(data []byte, level TruthLevel) *ValidationResult
}
