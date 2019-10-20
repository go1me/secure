//https://www.helplib.com/GitHub/article_155107
//https://github.com/phink-team/Cobaltstrike-MS17-010/blob/master/modules/pwndog.cna
package main
import (
	"fmt"
	"net"
	"time"
	"strings"
	"strconv"
)

type ip_target struct{
	net_card string
	be_scan bool
	alive bool
	is_getin bool
	port []int
}



func hosts(ipnet net.IPNet) ([]net.IP, error) {
	var ips []net.IP
	ip := ipnet.IP
	for ip := ip.Mask(ipnet.Mask); ipnet.Contains(ip); inc(ip) {
		ips = append(ips, ip)
	}
	return ips[1 : len(ips)-1], nil
}
	
func inc(ip net.IP) {
	for j := len(ip) - 1; j >= 0; j-- {
		ip[j]++
		if ip[j] > 0 {
			break
		}
	}
}


func Ips() (map[string]*ip_target,error){
	var ip_map=make(map[string]*ip_target)
    interfaces, err := net.Interfaces()
    if err != nil {
        return nil,err
    }
    for _, i := range interfaces {	
		if (i.Flags & net.FlagUp) == 0{
			continue
		}
        byName, err := net.InterfaceByName(i.Name)
        if err != nil {
            return nil,err
        }
        addresses, err := byName.Addrs()
        for _, v := range addresses {
			if ipnet, ok := v.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
				if ipnet.IP.To4() != nil {
					if  strings.Index(byName.Name, "蓝牙")==-1 && strings.Index(byName.Name, "Npcap Loopback Adapter")==-1{
						ip := ipnet.IP
						for ip := ip.Mask(ipnet.Mask); ipnet.Contains(ip); inc(ip) {
							ip_t:=new(ip_target)
							ip_t.net_card = byName.Name
							ip_map[ip.String()]=ip_t
							//fmt.Println(ip_map[ip.String()])
						}
					}
				}
			}
        }
    }
    return ip_map,nil
}



func main(){
	//ip_list := list.New()
	port_list := []int{139,445}
	fmt.Println("hello word")
	ip_map,_:=Ips()
	for i,_ := range(ip_map){

		if i != "192.168.34.132" && i != "10.10.10.117"{
			delete(ip_map,i)
			continue
		}
		
		for _,port :=range(port_list){
			_, err  := net.DialTimeout("tcp", i+":"+strconv.Itoa(port), time.Second*3)
 
            if err != nil{
                continue
			}
			ip_map[i].port = append(ip_map[i].port,port)
			//fmt.Println(ip_map[i])
		}
		
	}
	for i,v := range(ip_map){

		fmt.Println(i,v)
	}



	
	
	
}
