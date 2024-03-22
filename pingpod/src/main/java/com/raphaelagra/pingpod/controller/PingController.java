package com.raphaelagra.pingpod.controller;

import java.net.InetAddress;
import java.net.UnknownHostException;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PingController {

	@GetMapping("/ping")
    public String ping() throws UnknownHostException {
        String podName = InetAddress.getLocalHost().getHostName();
        return "Pong! This pod's name is: " + podName;
    }
}
