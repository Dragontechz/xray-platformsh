package main

import (
	"io"
	"log"
	"net"
	"os"
)

func main() {
	target := os.Getenv("TARGET_HOST")
	if target == "" {
		log.Fatal("TARGET_HOST must be set")
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	listener, err := net.Listen("tcp", "0.0.0.0:"+port)
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	log.Printf("tcp proxy listening on :%s, forwarding to %s", port, target)

	for {
		client, err := listener.Accept()
		if err != nil {
			log.Printf("accept: %v", err)
			continue
		}
		go handle(client, target)
	}
}

func handle(client net.Conn, target string) {
	defer client.Close()

	upstream, err := net.Dial("tcp", target)
	if err != nil {
		log.Printf("dial %s: %v", target, err)
		return
	}
	defer upstream.Close()

	done := make(chan struct{}, 2)
	go func() {
		io.Copy(upstream, client)
		done <- struct{}{}
	}()
	go func() {
		io.Copy(client, upstream)
		done <- struct{}{}
	}()
	<-done
}
