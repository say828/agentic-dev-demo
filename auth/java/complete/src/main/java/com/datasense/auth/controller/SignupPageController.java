package com.datasense.auth.controller;

import com.datasense.auth.domain.SignupResult;
import com.datasense.auth.service.OtpService;
import com.datasense.auth.service.SignupService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * 회원가입 OTP 화면(Thymeleaf). REST(/auth/*)와 동일한 서비스를 재사용해
 * 발급 → 인증번호 입력 → 결과까지 브라우저에서 직접 확인한다.
 * 01_planning의 EARS 명세(AC-1~AC-6)가 실제 동작 화면으로 이어짐을 보여주는 자리다.
 */
@Controller
public class SignupPageController {

    private static final String PURPOSE = "signup";

    private final OtpService otpService;
    private final SignupService signupService;

    public SignupPageController(OtpService otpService, SignupService signupService) {
        this.otpService = otpService;
        this.signupService = signupService;
    }

    /** 1단계: 이메일 입력 화면. */
    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("step", "email");
        return "signup";
    }

    /** 2단계: OTP 발급 후 '인증번호 입력' 화면. 데모 편의상 발급 code를 노출한다(AC-1). */
    @PostMapping("/issue")
    public String issue(@RequestParam(required = false) String email, Model model) {
        String normalized = email == null ? "" : email.trim();
        if (normalized.isEmpty()) {
            model.addAttribute("step", "email");
            model.addAttribute("error", "이메일을 입력하세요.");
            return "signup";
        }
        String code = otpService.issue(normalized, PURPOSE);
        model.addAttribute("step", "otp");
        model.addAttribute("email", normalized);
        model.addAttribute("issuedCode", code); // 데모: 실제로는 이메일로 전송한다
        return "signup";
    }

    /** 3단계: OTP 검증 + 가입. 결과(성공/거부 사유)를 화면에 표시한다(AC-2~AC-5). */
    @PostMapping("/verify")
    public String verify(@RequestParam String email,
                         @RequestParam(required = false) String otp,
                         Model model) {
        String code = otp == null ? "" : otp.trim();
        SignupResult result = signupService.signup(email, code, PURPOSE, null);
        model.addAttribute("step", "result");
        model.addAttribute("email", email);
        model.addAttribute("result", result);
        model.addAttribute("reasonText", reasonText(result.reason()));
        return "signup";
    }

    /** OTP 검증 사유 코드를 강의용 한국어 문장으로 변환한다. */
    private String reasonText(String reason) {
        return switch (reason) {
            case "ok" -> "인증에 성공해 계정을 생성했습니다.";
            case "no_otp" -> "발급된 인증번호가 없습니다. 처음부터 다시 진행하세요.";
            case "wrong_code" -> "인증번호가 일치하지 않습니다.";
            case "expired" -> "인증번호가 만료되었습니다(발급 후 300초 초과).";
            case "locked" -> "인증번호를 5회 이상 틀려 잠겼습니다.";
            default -> reason;
        };
    }
}
